import sqlite3
from .connection import conn
import json


def get_properties(target_class):  # 获取指定classes的properties
    c = conn.cursor()
    # 执行查询
    c.execute("SELECT property FROM properties WHERE class=? ORDER BY rank ASC", (target_class,))
    result_list = c.fetchall()
    real_result = [item[0] for item in result_list]
    return real_result


def get_property_info(target_class, target_property):  # 获取指定property的form、range和comment
    c = conn.cursor()
    c.execute("SELECT form,range,comment FROM properties WHERE class=? AND property=?", (target_class, target_property))
    return c.fetchone()


def get_properties_info(target_class):  # 获取指定class的property及其form、range和comment
    c = conn.cursor()
    c.execute("SELECT property,form,range,comment FROM properties WHERE class=? ORDER BY rank ASC", (target_class,))
    return c.fetchall()


def check_property_name_exist(i_class, i_property):
    # 查看名称是否存在，存在返回true，不存在返回false
    c = conn.cursor()
    c.execute("SELECT property FROM properties WHERE class=? AND property=?", (i_class, i_property))
    row = c.fetchone()
    if row is not None:
        return True
    else:
        return False


def new_property(i_class, i_property, i_form, i_range, i_comment):  # 新建property
    if check_property_name_exist(i_class, i_property):
        return False, {'reason': 'name exists'}
    try:
        with conn:
            c = conn.cursor()
            c.execute('''INSERT INTO properties (class, property, form, range, comment, rank)
                        VALUES (?, ?, ?, ?, ?, (SELECT COALESCE(MAX(rank), 0) + 1 FROM properties WHERE class=?))''',
                      (i_class, i_property, i_form, i_range, i_comment, i_class))
    except sqlite3.Error as e:
        print('new_property发生错误，原始日志：', e)
        return False, {'reason': 'exe failed'}
    else:
        return True, ''


def change_property(i_class, i_property, i_range, i_comment):  # 更新property详情
    try:
        with conn:
            # 需要检查变更property后所有元素是否都还符合要求
            property_info = get_property_info(i_class, i_property)
            property_form = property_info[0]
            c = conn.cursor()
            c.execute('''SELECT name,properties FROM items WHERE class=?''', (i_class, ))
            items = c.fetchall()
            if items:
                for i in items:
                    p = json.loads(i[1])
                    if i_property in p.keys():  # 保证这个属性存在
                        data = p[i_property]
                        if property_form == 'list':
                            if data != '' and data not in i_range.split(','):  # 属性选择不为空，且没在新列表内
                                return False, {'reason':'still using'}
                        elif property_form == 'num':
                            min_num = float(i_range.split('-')[0])
                            max_num = float(i_range.split('-')[1])
                            if data != '':  # 得确保有数
                                data = float(data)
                                if min_num > data or max_num < data:
                                    return False, {'reason': 'out range'}
            # 更新property
            c.execute('''UPDATE properties SET range=?,comment=? WHERE class=? AND property=?''', (i_range, i_comment, i_class, i_property))
    except sqlite3.Error as e:
        return False, {'reason': 'exe failed'}
    else:
        return True, ''


def manage_all_properties(i_class, properties):  # 管理property，properties参数为仅property组成的有序列表，该函数只负责删除或变更位置
    old_properties = get_properties(i_class)
    # print('old_properties', old_properties)
    del_properties = [p for p in old_properties if p not in properties]  # 获取需要删除的属性
    if len(del_properties):
        try:
            with conn:
                # 需要先把有该属性的内容删掉
                c = conn.cursor()
                c.execute('''SELECT id,properties FROM items WHERE class=?''', (i_class,))
                items = c.fetchall()
                for item in items:
                    item_properties = json.loads(item[1])
                    changed_flag = False
                    for key in del_properties:
                        if key in item_properties:  # 与item_properties.keys()等效
                            del item_properties[key]
                            changed_flag = True
                    if changed_flag:
                        c.execute('''UPDATE items SET properties=? WHERE id=?''', (json.dumps(item_properties, ensure_ascii=False), item[0]))
                # 然后删除属性
                c.executemany("DELETE FROM properties WHERE class=? AND property=?",
                              [(i_class, p) for p in del_properties])
        except sqlite3.Error as e:
            print('manage_all_property发生错误，原始日志：', e, del_properties)
            return False, {'reason': 'del error'}
    try:
        with conn:
            c = conn.cursor()
            rank = 1
            for p in properties:
                c.execute("UPDATE properties SET rank=? WHERE class=? AND property=?", (rank, i_class, p))
                rank += 1
    except sqlite3.Error as e:
        print('manage_all_class发生错误，原始日志：', e, '参数：', rank, i_class, p)
        return False, {'reason': 'rank error'}
    return True, ''
