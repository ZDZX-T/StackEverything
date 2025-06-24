from browser import document, window, html, ajax, timer # type: ignore
from universal import my_alert, my_success, disable_selection, enable_selection, config, Promise
from i18n import i18n
import json
import time


########
# 元素详情模态框
def remove_invalid_tip():  # 移除输入框的感叹号
    document['new_item_name'].classList.remove('is-invalid')
    document['new_item_class'].classList.remove('is-invalid')
    property_divs = document['new_item_property_area'].children
    for num in range(len(property_divs)):
        document[f'property_{num+1}'].classList.remove('is-invalid')
    document['new_item_is_virtual'].classList.remove('is-invalid')
    document['new_item_expiration_time'].classList.remove('is-invalid')
    document['new_item_comment'].classList.remove('is-invalid')


def load_new_item_properties(db_data, item_properties={}):  # 根据给定properties数据去渲染页面properties内容
    counter = 1  # 和rank从1开始契合
    for i in db_data:
        new_div = html.DIV()
        if i != db_data[-1]:  # 决定div要不要加mb-2的class
            new_div.classList.add('mb-2')
        new_div <= html.LABEL(f'{i[0]}', **{'for': f"property_{counter}", 'class': "ps-2 form-label mb-1", 'data-form': i[1]})
        if i[1] == 'list':
            new_select  = html.SELECT(Class="form-select", id=f"property_{counter}")
            new_select <= html.OPTION(i18n['oa_please_select'], value="", selected="")  # "请选择"
            options = i[2].split(',')
            for op_num in range(len(options)):
                new_select <= html.OPTION(f'{options[op_num]}', value=f'{options[op_num]}')
            if new_div.text in item_properties.keys():
                new_select.value = item_properties[new_div.text]
            new_div <= new_select
        elif i[1] == 'num':
            new_input = html.INPUT(type="number", Class="form-control", id=f"property_{counter}", placeholder=f"{i[2]}")
            if new_div.text in item_properties.keys():
                new_input.value = item_properties[new_div.text]
            new_div <= new_input
        new_div <= html.DIV(Class='invalid-feedback', id=f'property_{counter}_feedback')
        document['new_item_property_area'] <= new_div
        counter += 1


def get_new_item_properties(ev=None):  # 分类选定后，加载属性
    target_class = document['new_item_class'].value
    # print(f'DBG：触发加载【{target_class}】属性')
    document['new_item_property_area'].html = ''
    if target_class == '':
        return
    def on_complete(req):
        if req.status != 200:
            my_alert(i18n['oa_load_class_error'])# ('加载分类数据失败！')  
            return
        data = json.loads(req.text)
        # print(f'DBG：属性原始数据{data}')
        if data['status'] == 'success':
            data = data['data']
            load_new_item_properties(data)
        else:
            my_alert(data['message'])
    ajax.get('/operating_area/get_properties', data={'target_class': target_class}, oncomplete=on_complete)


def show_item_info(target_id):  # 加载元素详情
    print('DBG：渲染元素信息')
    def load_item_info(data):
        item_info = data['item']
        classes = data['classes']
        properties = data['properties']
        # 表头
        document['add_item_form_title'].text = f'【{item_info['name']}】{i18n["ub_item_info_details"]}'  # '详情'
        document['add_item_form_title'].attrs['data-id'] = item_info['id']
        # 图片
        if item_info['img'] != '':
            document['cropped_img'].src = '/uploaded_pic/' + item_info['img']
            document['cropped_img_area'].style.display = 'block'
        # 名称
        document['new_item_name'].value = item_info['name']
        # 加载classes
        document['new_item_class'].unbind()  # 避免误触发加载properties
        document['new_item_class'].html = ''
        document['new_item_class'] <= html.OPTION(i18n['oa_please_select'], value="", disabled="", selected="")  # "请选择"
        for i in classes:
            document['new_item_class'] <= window.Option.new(f"{i}", f"{i}")
        document['new_item_class'].value = item_info['class']
        document['new_item_class'].bind('change', get_new_item_properties)  # 恢复绑定
        # 加载properties
        item_properties = json.loads(item_info['properties'])
        load_new_item_properties(properties, item_properties)
        # 加载is_virtual
        if item_info['is_virtual'] == 1:
            document['new_item_is_virtual_true'].checked = True
        # 加载expiration_time
        document['new_item_expiration_time'].value = item_info['expiration_time']
        # 加载comment
        document['new_item_comment'].value = item_info['comment']
        # 更改按钮可见性
        # document['btn_item_delete'].text = '删除(含子物品)' if item_info['have_children'] else '删除'
        document['btn_item_delete'].text = i18n['ub_del_include_child'] if item_info['have_children'] else i18n['ub_del']
        document['btn_item_add_change'].text = i18n['ub_update']  # '更新'
        document['btn_item_delete'].style.display = 'block'
    get_item_info(target_id).then(
        lambda data: load_item_info(data)
    ).catch(
        lambda msg: my_alert(msg)
    )
    document['only_open_change_item_form'].click()  # 如果加载顺序有问题，后期可以考虑将其放置于确认加载了数据之后


def get_item_info(id):  # 获取给定id的全部item内容
    def executor(resolve, reject):
        def on_complete(req):
            if req.status != 200:
                my_alert(i18n['oa_get_item_info_failed'])  # ('获取元素信息失败！')
                return
            data = json.loads(req.text)
            # print(f'DBG：get_item_info获取的原始item内容{data}')
            if data['status'] == 'success':
                resolve(data)
            else:
                reject(data['message'])
        ajax.get(f'/operating_area/get_item_info', data={'id': id}, oncomplete=on_complete)
    return Promise(executor)


def add_change_item(parentID):  # 新增/更新元素
    def executor(resolve, reject):
        # 禁用提交按钮，避免重复提交
        document['btn_item_add_change'].disabled = True
        remove_invalid_tip()
        data = {
            'id': document['add_item_form_title'].attrs['data-id'],
            'name': document['new_item_name'].value,
            'auto_rename': document['new_item_name_auto_rename'].checked,
            'class': document['new_item_class'].value,
            'properties': {},  # 比较复杂，等会儿读
            'is_virtual': document['new_item_is_virtual_true'].checked == True,
            'parent': parentID,
            'comment': document['new_item_comment'].value,
            'expiration_time': document['new_item_expiration_time'].value,
            'img_data': ''  # 稍后录入
        }
        property_divs = document['new_item_property_area'].children
        for num in range(len(property_divs)):
            div = property_divs[num]
            rank = num + 1  # 数据库的rank值
            label = div.getElementsByTagName('label')[0]
            property_name = label.text
            property_value = document[f'property_{rank}'].value
            if label.attrs['data-form'] == 'num' and property_value != '':
                property_value = float(property_value)
            data['properties'][property_name] = property_value
        if document['cropped_img_area'].style.display == 'block':
            if ',' in document['cropped_img'].src:  # 说明上传了新图片
                data['img_data'] = document['cropped_img'].src.split(',')[1]
            else:  # 说明是更新
                data['img_data'] = document['cropped_img'].getAttribute('src').replace('/uploaded_pic/', '')
        # print(f'DBG：获取的原始新增元素数据{data}')
        have_error = False
        if data['name'] == '':
            document['new_item_name_feedback'].text = i18n['ub_name_cant_empty']  # '名称不能为空'
            document['new_item_name'].classList.add('is-invalid')
            have_error = True
        if data['class'] == '':
            document['new_item_class_feedback'].text = i18n['new_item_class_feedback']  # '请选择分类'
            document['new_item_class'].classList.add('is-invalid')
            have_error = True
        if have_error:
            document['btn_item_add_change'].disabled = False
        else:
            modal_local_data = data
            def on_complete(req):
                nonlocal modal_local_data
                if req.status != 200:
                    my_alert(req.status)
                else:
                    data = json.loads(req.text)
                    if data['status'] == 'success':
                        if modal_local_data['id'] == '':
                            my_success(i18n['ub_successfully_added'])  # ('新增成功')
                            resolve({'mode': 'oa_add', 
                                     'target_id': 0, 
                                     'id': data['id'], 
                                     'filename': data['img_path'], 
                                     'name': data['name']
                                     })
                        else:
                            my_success(i18n['ub_successfully_change'])  # ('修改成功')
                            if document['page_operating_area'].style.display == 'block':  # 正在操作区
                                resolve({'mode': 'oa_change'})
                            elif document['page_view_items'].style.display == 'block':  # 正在物品浏览区
                                resolve({'mode': 'vi_change'})
                        document['close_add_change_item_form'].click()  # 关闭窗口
                    elif data['status'] == 'error':
                        my_alert(f'{i18n["ub_op_failt"]}{data["message"]}')  # '操作失败，'
                    elif data['status'] == 'questions':
                        for i in data['questions']:
                            document[f'{i['target_dom_id']}_feedback'].text = i['message']
                            document[i['target_dom_id']].classList.add('is-invalid')
                    else:
                        my_alert(i18n['ub_packet_broken'])  # ('返回包数据损坏')
                document['btn_item_add_change'].disabled = False  # resolve不会阻止下方代码运行
            data = json.dumps({'data': data}, ensure_ascii=False)
            # print(f'DBG：提交的数据{data}')
            ajax.post('/operating_area/add_change_item', data=data, 
                    headers={"Content-Type": "application/json"}, oncomplete=on_complete)
    return Promise(executor)