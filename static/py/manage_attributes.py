from flask import Blueprint, request, jsonify, current_app
import SQL
import json
import logging
from ..bry.i18n import i18n


manage_attributes = Blueprint('manage_attributes', __name__)


@manage_attributes.route('/manage_attributes/get_classes')  # 拉取分类
def get_classes():
    classes = SQL.get_classes()
    # current_app.logger.info('↓get_classes拉取分类结果'+str(classes))
    return jsonify({'classes': classes})


@manage_attributes.route('/manage_attributes/get_properties')  # 拉取分类的属性
def get_properties():
    target_class = request.args.get('target_class', None)
    if target_class is not None:
        properties = SQL.get_properties(target_class)
        # current_app.logger.info('↓get_properties拉取分类的属性结果'+str(properties))
        return jsonify({'status': 'success', 'properties': properties})
    else:
        return jsonify({'status': 'error','message': i18n['oa_miss_class']})  # "未找到参数target_class"
    

@manage_attributes.route('/manage_attributes/add_class', methods=['POST'])  # 新增分类
def add_class():
    data = request.get_json()
    target_class = data.get('target_class', None)
    if target_class is not None:
        is_success, info = SQL.new_class(target_class)
        if is_success:
            current_app.logger.info('↓add_class新增分类成功，新分类'+str(target_class))
            return jsonify({'status': 'success', 'new_class': target_class})
        else:
            if info['reason'] == 'name exists':
                ret_info = i18n['new_item_name_feedback']  # '名称已存在'
            else:
                ret_info = i18n['oa_db_fault']+info['data']  # '数据库执行出错'
            current_app.logger.info('↓add_class新增分类失败，原因为'+str(ret_info))
            return jsonify({'status': 'error', 'message': ret_info})
    else:
        return jsonify({'status': 'error', 'message': i18n['oa_miss_class']})  # '未找到参数target_class'


@manage_attributes.route('/manage_attributes/manage_classes', methods=['POST'])  # 传入当前classes列表进行排序、删除
def manage_classes():
    data = request.get_json()
    classes = data.get('classes', None)
    if classes is not None:
        is_success, info = SQL.manage_all_class(classes)
        if is_success:
            current_app.logger.info('↓manage_classes管理分类成功，数据为'+str(classes))
            return jsonify({'status': 'success'})
        else:
            if info['reason'] == 'del error':
                ret_info = i18n['ma_class_del_error']  # '删除出错，可能仍有物品使用要删除的分类'
            else:
                ret_info = i18n['ma_rank_error']  # '变更rank出错'
            current_app.logger.info('↓manage_classes管理分类失败，原因为'+str(ret_info))
            return jsonify({'status': 'error', 'message': ret_info})
    else:
        return jsonify({'status': 'error', 'message': i18n['ma_miss_classes']})  # '缺失classes参数'
    

@manage_attributes.route('/manage_attributes/add_property', methods=['POST'])  # 新增属性
def add_property():
    data = request.get_json()
    target_class = data.get('target_class', None)
    new_property_name = data.get('new_property_name', None)
    new_property_form = data.get('new_property_form', None)
    new_property_range = data.get('new_property_range', None)
    new_property_comment = data.get('new_property_comment', None)
    if any(i is None for i in [target_class, new_property_name, new_property_form, new_property_range, new_property_comment]):
        return jsonify({'status': 'error', 'message': i18n['ma_miss_parameter']})  # "缺少参数"
    is_success, info = SQL.new_property(target_class, new_property_name, new_property_form, new_property_range, new_property_comment)
    if is_success:
        current_app.logger.info(f'↓add_property新增属性成功，分类【{target_class}】,名称【{new_property_name}】，类型【{new_property_form}】，范围【{new_property_range}】，备注【{new_property_comment}】')
        return jsonify({'status': 'success', 'new_property_name': new_property_name})
    else:
        if info['reason'] == 'name exists':
            ret_info = i18n['ma_name_exists']  # '名称已存在'
        else:
            ret_info = i18n['oa_db_fault']  # '数据库执行出错'
        current_app.logger.info(f'↓add_property新增属性失败，原因为{ret_info}')
        return jsonify({'status': 'error', 'message': ret_info})
    

@manage_attributes.route('/manage_attributes/change_property', methods=['POST'])  # 修改属性
def change_property():
    data = request.get_json()
    target_class = data.get('target_class', None)
    target_property = data.get('target_property', None)
    new_property_range = data.get('new_property_range', None)
    new_property_comment = data.get('new_property_comment', None)
    if any(i is None for i in [target_class, target_property, new_property_range, new_property_comment]):
        return jsonify({'status': 'error', 'message': i18n['ma_miss_parameter']})  # "缺少参数"
    is_success, info = SQL.change_property(target_class, target_property, new_property_range, new_property_comment)
    if is_success:
        current_app.logger.info(f'↓change_property修改属性成功，分类【{target_class}】,名称【{target_property}】，范围【{new_property_range}】，备注【{new_property_comment}】')
        return jsonify({'status': 'success'})
    else:
        if info['reason'] == 'still using':
            ret_info = i18n['ma_del_using_property']  # '有物品将使用不存在的属性，请先更改物品属性'
        elif info['reason'] == 'out range':
            ret_info = i18n['ma_property_out_range']  # '有物品的属性超出新设范围，请先更改物品属性'
        else:
            ret_info = i18n['oa_db_fault']  # '数据库执行出错'
        current_app.logger.info(f'↓change_property修改属性失败，原因为{ret_info}')
        return jsonify({'status': 'error', 'message': ret_info})
    

@manage_attributes.route('/manage_attributes/manage_properties', methods=['POST'])  # 传入当前properties列表进行排序、删除
def manage_properties():
    data = request.get_json()
    target_class = data.get('target_class', None)
    properties = data.get('properties', None)
    if any(i is None for i in [target_class, properties]):
        return jsonify({'status': 'error', 'message': i18n['ma_miss_parameter']})  # "缺少参数"
    is_success, info = SQL.manage_all_properties(target_class, properties)
    if is_success:
        current_app.logger.info(f'↓manage_properties属性管理成功')
        return jsonify({'status': 'success'})
    else:
        if info['reason'] == 'del error':
            ret_info = i18n['ma_property_del_error']  # '删除出错'
        else:
            ret_info = i18n['ma_rank_error']  # '变更rank出错'
        current_app.logger.info(f'↓manage_properties属性管理失败，原因为{ret_info}')
        return jsonify({'status': 'error', 'message': ret_info})
        

@manage_attributes.route('/manage_attributes/get_property_info', methods=['POST'])  # 获取属性详情
def get_property_info():
    data = request.get_json()
    target_class = data.get('target_class', None)
    target_property = data.get('target_property', None)
    if target_class is not None and target_property is not None:
        property_info = SQL.get_property_info(target_class, target_property)
        return jsonify({'status': 'success', 'form': property_info[0], 'range': property_info[1], 'comment': property_info[2]})
    else:
        return jsonify({'status': 'error', 'message': i18n['ma_miss_parameter']})  # "缺少参数"
