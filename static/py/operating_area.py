from flask import Blueprint, request, jsonify, current_app
import SQL
import json
from PIL import Image
import base64
import io
import os
import config
import time
from ..bry.i18n import i18n


operating_area = Blueprint('operating_area', __name__)


def get_item_path(id):  # 根据id获取路径（不包含0号节点）
    path = []
    got_ids = []  # 兜底，防止成环后死机
    while int(id) != 0:
        ret = SQL.get_item(int(id))
        if ret is None:
            return jsonify({'status': 'error', 'message': f'id{id}{i18n["oa_db_no_ret"]}'})  # '数据库未返回内容'
        if int(id) in got_ids:
            return jsonify({'status': 'error', 'message': i18n['oa_db_break']})  # f'数据库已损坏，请手工修复数据库或重新建立数据库'
        path.append((ret['name'], int(id)))
        got_ids.append(int(id))
        id = ret['parent']
    # path.append(('/', 0))
    path = path[::-1]
    return path


@operating_area.route('/operating_area/get_breadcrumb_path')  # 根据id获取面包屑路径
def get_breadcrumb_path():
    id = request.args.get('id', None)
    if id is not None:
        try:  # 防止get_item_path返回错误内容
            path = [('/', 0)] + get_item_path(id)
        except TypeError:
            return jsonify({'status': 'error', 'message': f'{i18n["oa_get_path_failed_1"]}{id}{i18n["oa_get_path_failed_2"]}'})  # f'获取id {id}路径失败'
        else:

            return jsonify({'status': 'success', 'data': path})
    else:
        return jsonify({'status': 'error','message': i18n['oa_miss_id']})  # '未找到参数id'
    

@operating_area.route('/operating_area/name2id')  # 根据名称获取物品id
def name2id():
    name = request.args.get('name', None)
    if name is not None:
        item_id = SQL.item_name2id(name)
        if item_id == -1:
            return jsonify({'status': 'warning', 'message': f'{i18n["oa_item_not_find"]}【{name}】'})  # '未找到物品'
        else:
            return jsonify({'status': 'success', 'id': item_id})
    else:
        return jsonify({'status': 'error','message': i18n['oa_miss_id']})  # '未找到参数id'


@operating_area.route('/operating_area/get_item_info')  # 获取元素详细信息
def get_item_info():
    id = request.args.get('id', None)
    if id is not None:
        ret = SQL.get_item(id)
        if ret is None:
            return jsonify({'status': 'error', 'message': i18n['oa_db_no_ret']})  # '数据库未返回内容'
        else:
            classes = SQL.get_classes()
            properties = SQL.get_properties_info(ret['class'])
            return jsonify({'status': 'success', 'item': ret, 'classes': classes, 'properties': properties})
    else:
        return jsonify({'status': 'error','message': i18n['oa_miss_id']})  # '未找到参数id'
    

@operating_area.route('/operating_area/get_children')  # 获取元素子元素
def get_children():
    id = request.args.get('id', None)
    if id is not None:
        ret = SQL.get_children(id)
        if ret is None:
            return jsonify({'status': 'error', 'message': i18n['oa_db_no_ret']})  # '数据库未返回内容'
        else:
            return jsonify({'status': 'success', 'data': ret})
    else:
        return jsonify({'status': 'error','message': i18n['oa_miss_id']})  # '未找到参数id'
    

@operating_area.route('/operating_area/get_properties')  # 获取指定class的properties信息
def get_properties():
    target_class = request.args.get('target_class', None)
    if target_class is not None:
        ret = SQL.get_properties_info(target_class)
        if ret is None:
            return jsonify({'status': 'error', 'message': i18n['oa_db_no_ret']})  # '数据库未返回内容'
        else:
            return jsonify({'status': 'success', 'data': ret})
    else:
        return jsonify({'status': 'error','message': i18n['oa_miss_class']})  # '未找到参数target_class'
    

@operating_area.route('/operating_area/move_item', methods=['POST'])  # 移动元素
def move_item():
    data = request.get_json()
    from_id = data.get('from_id', None)
    to_id = data.get('to_id', None)
    mode = data.get('mode', None)
    if from_id is None or to_id is None or mode is None:
        current_app.logger.info(f'↓move_item移动元素失败，原因为缺失参数')
        return jsonify({'status': 'error', 'message': i18n['oa_miss_parameter']})  # '缺失参数'
    else:
        # 成环监测
        to_path = get_item_path(to_id)
        for i in to_path:
            if i[1] == int(from_id):  # 存在环
                current_app.logger.info(f'↓move_item移动元素失败，原因为路径成环')
                return jsonify({'status': 'special_error','message': i18n['oa_path_loop']})  # '严重错误：路径成环'
        # 与SQL交互
        from_info = SQL.get_item(int(from_id))
        to_info = SQL.get_item(int(to_id))  # to_id不可能是0，因为根目录一直有元素
        if from_info is None or to_info is None:
            current_app.logger.info(f'↓move_item移动元素失败，原因为未找到所操作的元素（id为{from_id}或{to_id}）')
            return jsonify({'status': 'error', 'message': i18n['oa_element_not_find']})  # '未找到所操作的元素'
        else:
            if mode == 'i':
                is_success = SQL.move_item(from_info['id'], from_info['parent'], from_info['sibling'], to_info['id'], 0)
            elif mode == 'l':
                is_success = SQL.move_item(from_info['id'], from_info['parent'], from_info['sibling'], to_info['parent'], to_info['sibling'])
            elif mode == 'r':
                is_success = SQL.move_item(from_info['id'], from_info['parent'], from_info['sibling'], to_info['parent'], to_info['id'])
            else:
                current_app.logger.info(f'↓move_item移动元素失败，原因为非法模式{mode}')
                return jsonify({'status': 'error', 'message': f'{i18n["oa_invalid_mode"]}{mode}'})  # '非法模式'
            if is_success:
                current_app.logger.info(f'↓move_item移动元素成功，{from_id}移动到{to_id}的{mode}')
                return jsonify({'status': 'success'})
            else:
                current_app.logger.info(f'↓move_item移动元素失败，原因为数据库执行出错')
                return jsonify({'status': 'error', 'message': i18n['oa_db_fault']})  # '数据库执行出错'


@operating_area.route('/operating_area/del_item', methods=['POST'])  # 删除元素
def del_item():
    data = request.get_json()
    id = data.get('id', None)
    if id is not None:
        is_success, info = SQL.del_item(id)  # info返回的删除物品个数，因为可能存在递归删除
        if is_success:
            current_app.logger.info(f'↓del_item删除元素成功，删除的元素有{len(info)}个，数据为{str(info)}')
            return jsonify({'status': 'success', 'removed_id': id, 'del_count': len(info)})
        else:
            ret_info = i18n['oa_no_id_info_1']+str(id)+i18n['oa_no_id_info_2']  # f'无id为{id}的元素信息'
            current_app.logger.info(f'↓del_item删除元素失败，原因为{ret_info}')
            return jsonify({'status': 'error', 'message': ret_info})
    else:
        current_app.logger.info(f'↓del_item删除元素失败，原因为未找到参数id')
        return jsonify({'status': 'error', 'message': i18n['oa_miss_id']})  # "未找到参数id"


@operating_area.route('/operating_area/add_change_item', methods=['POST'])  # 增加/更新元素
def add_change_item():
    data = request.get_json()
    data = data.get('data', None)
    if data is not None:
        questions = []
        if data['id'] == '':  # 新建元素
            if SQL.check_item_name_exist(data['name']):
                rename = SQL.get_available_item_name(data['name'])
                if data['auto_rename']:  # 自动重命名开
                    data['name'] = rename
                else:  # 提示重名
                    questions.append({'message': f'{i18n["oa_name_exist"]}{rename}', 'target_dom_id': 'new_item_name'})  # '名称已存在，一个可用名称是'
        else:  # 更新元素
            # 检查id是否存在
            old_item_info = SQL.get_item(int(data['id']))
            if old_item_info is not None:
                if old_item_info['name'] == data['name']:  # 名字没变
                    pass
                else:  # 名字变了，严查
                    if SQL.check_item_name_exist(data['name']):
                        rename = SQL.get_available_item_name(data['name'])
                        if data['auto_rename']:  # 自动重命名开
                            data['name'] = rename
                        else:  # 提示重名
                            questions.append({'message': f'{i18n["oa_name_exist"]}{rename}', 'target_dom_id': 'new_item_name'})  # '名称已存在，一个可用名称是'
        if not SQL.check_class_name_exist(data['class']):
            questions.append({'message': i18n['oa_class_not_exist'], 'target_dom_id': 'new_item_class'})  # '分类不存在'
        else:
            properties_info = SQL.get_properties_info(data['class'])
            properties = {}
            for i in properties_info:
                properties[i[0]] = {
                    'form': i[1],
                    'range': i[2],
                    'comment': i[3]
                }
            counter = 1
            for i in data['properties'].keys():
                if i not in properties.keys():
                    questions.append({'message': i18n['oa_property_not_exist'], 'target_dom_id': f'property_{counter}'})  # '属性不存在'
                else:
                    if data['properties'][i] != '':
                        if properties[i]['form'] == 'list':
                            if data['properties'][i] not in properties[i]['range'].split(','):
                                questions.append({'message': i18n['oa_select_out_range'], 'target_dom_id': f'property_{counter}'})  # '选项超出范围'
                        elif properties[i]['form'] == 'num':
                            min_num = float(properties[i]['range'].split('-')[0])
                            max_num = float(properties[i]['range'].split('-')[1])
                            try:
                                user_input_num = float(data['properties'][i])
                            except ValueError:
                                questions.append({'message': i18n['oa_need_value_1']+properties[i]["range"]+i18n['oa_need_value_2'], 'target_dom_id': f'property_{counter}'})
                                # f'请输入{properties[i]["range"]}的数值'
                            else:
                                if not (min_num <= user_input_num <= max_num):
                                    questions.append({'message': i18n['oa_need_value_1']+properties[i]["range"]+i18n['oa_need_value_2'], 'target_dom_id': f'property_{counter}'})
                                    # f'请输入{properties[i]["range"]}的数值'
                counter += 1
        if data['is_virtual'] != True and data['is_virtual'] != False:
            questions.append({'message': 'flag{Ple@se_D0_Not_Do_Thi5}', 'target_dom_id': f'new_item_is_virtual'})
        # 日期和备注有什么值得检查的吗？我不知道
        if len(questions) != 0:
            current_app.logger.info(f'↓add_change_item增加/更新元素失败，后端预检查存在一些问题，{str(questions)}')
            return jsonify({'status': 'questions', 'message': i18n['oa_backend_pre_check'], 'questions': questions})  # '后端预检查存在一些问题'
        else:
            try:
                if len(data['img_data']) < 30 and '_sm.jpg' in data['img_data']:  # 图片没更新
                    img_name = data['img_data']
                elif data['img_data'] != '':  # 有新图片
                    # 如果是更新的话，还要删除旧图片
                    if data['id'] != '' and old_item_info['img'] != '':
                        del_image_path = os.path.abspath(os.path.join(config.PIC_PATH,  old_item_info['img'].replace('_sm', '')))
                        del_thumbnail_path = os.path.abspath(os.path.join(config.PIC_PATH,  old_item_info['img']))
                        os.remove(del_image_path)
                        os.remove(del_thumbnail_path)
                    image_data = base64.b64decode(data['img_data'])
                    image = Image.open(io.BytesIO(image_data))
                    timestamp_ms = int(time.time() * 1000)
                    image_path = os.path.abspath(os.path.join(config.PIC_PATH,  f'{timestamp_ms}.jpg'))
                    image.save(image_path, format='JPEG', quality=100)
                    # 生成缩略图，没检查原大小是否大于缩略后边长
                    thumbnail = image.resize((config.PIC_SM_WIDTH, config.PIC_SM_WIDTH), Image.Resampling.LANCZOS)
                    thumbnail_name = f'{timestamp_ms}_sm.jpg'
                    thumbnail_path = os.path.abspath(os.path.join(config.PIC_PATH, thumbnail_name))
                    thumbnail.save(thumbnail_path, format='JPEG', quality=100)
                    img_name = thumbnail_name
                else:
                    img_name = ''
            except:
                current_app.logger.info(f'↓add_change_item增加/更新元素失败，原因为存储图片出错')
                return jsonify({'status': 'error', 'message': i18n['oa_img_storage_error']})  # '存储图片出错'
            else:
                if data['id'] == '':  # 新建元素
                    is_success, info = SQL.new_item(
                        i_name=data['name'],
                        i_class=data['class'],
                        i_properties=data['properties'],
                        i_is_virtual=data['is_virtual'],
                        i_parent=data['parent'],
                        i_img=img_name,  # 缩略图路径转大图路径好转，把_sm替换为空就行，所以存缩略图路径了
                        i_comment=data['comment'],
                        i_expiration_time=data['expiration_time']
                    )
                    if is_success:
                        current_app.logger.info(f'↓add_change_item新增元素成功，id{info}，名称{data["name"]}，图片路径{img_name}')
                        return jsonify({'status': 'success', 'id': info, 'name': data['name'], 'img_path': img_name})
                    else:
                        if info['reason'] == 'name exists':
                            ret_info =  i18n['oa_name_exists_1']+data['name']+i18n['oa_name_exists_2']  # f'物品名称【{data["name"]}】已存在'
                        else:
                            ret_info = i18n['oa_db_fault']+info['data']  # f'数据库执行出错，{info["data"]}'
                        current_app.logger.info(f'↓add_change_item新增元素失败，原因为{ret_info}')
                        return jsonify({'status': 'error', 'message': ret_info})
                else:  # 更新元素
                    is_success, info = SQL.alter_item(
                        i_id=int(data['id']),
                        i_name=data['name'],
                        i_class=data['class'],
                        i_properties=data['properties'],
                        i_is_virtual=data['is_virtual'],
                        i_img=img_name,
                        i_comment=data['comment'],
                        i_expiration_time=data['expiration_time']
                    )
                    if is_success:
                        current_app.logger.info(f'↓add_change_item修改元素成功')
                        return jsonify({'status': 'success', 'message': i18n['oa_change_item_success']})  # '修改元素成功'
                    else:
                        ret_info = i18n['oa_db_fault']+info['data']  # f'数据库执行出错，{info["data"]}'
                        current_app.logger.info(f'↓add_change_item修改元素失败，原因为{ret_info}')
                        return jsonify({'status': 'error', 'message': ret_info})
    else:
        current_app.logger.info(f'↓add_change_item增加/更新元素失败，原因为缺失data参数')
        return jsonify({'status': 'error', 'message': i18n['oa_miss_data']})  # '缺失data参数'