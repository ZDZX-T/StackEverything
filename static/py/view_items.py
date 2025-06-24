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


view_items = Blueprint('view_items', __name__)


@view_items.route('/view_items/get_db_data')  # 从数据库读取信息
def get_db_data():
    target_name = request.args.get('target_name', None)
    target_class = request.args.get('target_class', None)
    target_is_virtual = request.args.get('target_is_virtual', None)
    target_expiration_time = request.args.get('target_expiration_time', None)
    if target_name is None or target_class is None or target_is_virtual is None or target_expiration_time is None:
        return jsonify({'status': 'error','message': '缺失参数'})
    else:
        if target_class == '':  # 如果没有筛选class，那么将结果按照class排序
            classes = SQL.get_classes()
        else:
            classes = []
        db_data = SQL.get_items_with_filter(target_name, target_class, int(target_is_virtual), target_expiration_time, classes)
        if db_data is None:
            return jsonify({'status': 'error','message': i18n['vi_get_data_failed']})  # '拉取数据失败'
        else:
            # 获得了所需的数据信息，现在需要补充parent的真实名称
            parent_data = {0: '/'}  # id:名称
            for i in db_data.keys():
                if db_data[i]['parent'] in parent_data.keys():  # 有缓存记录
                    pass  # 有缓存就不管了
                else:  # 没有缓存，试着从db_data里找一找
                    if db_data[i]['parent'] in db_data.keys():  # db_data有，则更新parent_data缓存
                        parent_data[db_data[i]['parent']] = db_data[db_data[i]['parent']]['name']
                    else:  # 需要从数据库查名称了
                        single_data = SQL.get_item(db_data[i]['parent'])
                        if single_data is None:  # 寄了
                            return jsonify({'status': 'error','message': i18n['vi_get_parent_name_error_1']+str(db_data[i]["parent"])+i18n['vi_get_parent_name_error_2']})
                            # f'获取父元素名称时出错，无法查询到id为{db_data[i]["parent"]}的元素信息'
                        else:
                            parent_data[db_data[i]['parent']] = single_data['name']
                db_data[i]['parent_name'] = parent_data[db_data[i]['parent']]  # 到此处，能确保parent_data里有相关数据
                db_data[i]['properties'] = json.loads(db_data[i]['properties'])# 顺便把properties建立一下
            return jsonify({'status': 'success', 'db_data': db_data})

