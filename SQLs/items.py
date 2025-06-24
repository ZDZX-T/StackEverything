import sqlite3
import datetime
import json
import os
import config
from .connection import conn


RESERVED_WORD = ('/')  # 物品名称保留字


def check_item_name_exist(i_name):
    # 查看名称是否存在，存在返回true，不存在返回false
    if i_name in RESERVED_WORD: return False
    c = conn.cursor()
    c.execute("SELECT id FROM items WHERE name=?", (i_name,))
    row = c.fetchone()
    if row is not None:
        return True
    else:
        return False
        

def item_name2id(i_name):  # 物品名称->id，按理来说可以改造后与check_item_name_exist共用，后面再说
    if i_name in RESERVED_WORD: return 0
    c = conn.cursor()
    c.execute("SELECT id FROM items WHERE name=?", (i_name,))
    row = c.fetchone()
    if row is not None:
        return int(row[0])
    else:
        return -1
        

def get_available_item_name(i_name):  # 用以重名自动获取可用名称，按理来说可以改造后与check_item_name_exist共用，后面再说
    c = conn.cursor()
    c.execute('''SELECT name FROM items WHERE name=? OR name LIKE ? ORDER BY name  DESC LIMIT 1''', (i_name, f'{i_name}_%'))
    result = c.fetchone()
    if result:  # 提取编号
        last_name = result[0]
        if '_' in last_name:
            try:
                last_number = int(last_name.split("_")[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0
        # 有时候类似名称太多，会导致选不到想要的编号，因此还需要再检查一遍
        while check_item_name_exist(f'{i_name}_{last_number+1}'):
            last_number += 1
        return f'{i_name}_{last_number+1}'
    else:
        return i_name
        

def get_item(i_id):  # 获取物品信息
    try:
        c = conn.cursor()
        c.execute('''SELECT id, name, class, properties, is_virtual, 
                    parent, previous_parent, sibling, img, comment, 
                    setting_time, expiration_time FROM items WHERE id=?''', (i_id,))
        item = c.fetchone()
        if item is None:
            return None
        c.execute('''SELECT id FROM items WHERE parent=? LIMIT 1''', (item[0],))
        children_id1 = c.fetchone()
        ret = {
            'id': item[0],
            'name': item[1],
            'class': item[2],
            'properties': item[3],
            'is_virtual': item[4], 
            'parent': item[5],
            'previous_parent': item[6],
            'sibling': item[7],
            'img': item[8],
            'comment' : item[9],
            'setting_time': item[10],
            'expiration_time': item[11],
            'have_children': False if children_id1 is None else True  # 是否有子节点
        }
        return ret
    except sqlite3.Error as e:
        print('get_item()发生错误，原始日志：', e)
        return None
    

def get_items_with_filter(name_like, i_class, is_virtual, expiration_time, classes=[]):  # 根据要求筛选符合的items
    query = "SELECT id,name,class,properties,parent,img,comment,expiration_time FROM items WHERE 1=1"
    params = []
    if name_like != '':
        query += ' AND name LIKE ?'
        params.append(f'%{name_like}%')
    if i_class != '':
        query += ' AND class=?'
        params.append(i_class)
    if is_virtual != -1:
        query += ' AND is_virtual=?'
        params.append(is_virtual)
    if expiration_time != '':
        query += " AND expiration_time<=? AND expiration_time<>''"
        params.append(expiration_time)
    if len(classes) != 0:
        query += ' ORDER BY CASE class'
        for class_index in range(len(classes)):
            query += f" WHEN '{classes[class_index]}' THEN {class_index+1}"
        query += ' ELSE 0 END'
    try:
        c = conn.cursor()
        c.execute(query, params)
        result = c.fetchall()
        ret = {}  # ODOT 已验证确实能根据class排序，但是经过jsonify和loads后将破坏顺序，暂不管
        for i in result:
            ret[str(i[0])] = {  # 似乎经过jsonify和loads后，键的int就会变为str，所以干脆明确一点，从开始就是str
                'name': i[1],
                'class': i[2],
                'properties': i[3],
                'parent': i[4],
                'img': i[5],
                'comment': i[6],
                'expiration_time': i[7]
            }
        return ret
    except sqlite3.Error as e:
        print('get_items_with_filter()发生错误，原始日志：', e)
        return None


def new_item(i_name, i_class, i_properties, i_is_virtual, i_parent, i_img, i_comment, i_expiration_time):  # 新建物品
    # 检查重名
    if check_item_name_exist(i_name):
        return False, {'reason': 'name exists'}
    # 新建条目
    i_setting_time = datetime.datetime.now().isoformat()
    # 做一些兜底
    if i_properties == '':
        i_properties = {}
    try:
        with conn:
            c = conn.cursor()
            c.execute('''SELECT id FROM items WHERE parent=? AND sibling=?''', (i_parent, 0))  # 查找顶部元素id
            top_item = c.fetchone()
            c.execute('''INSERT INTO items 
                    (name, class, properties, is_virtual, parent, previous_parent, sibling, img, comment, setting_time, expiration_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (i_name, i_class, json.dumps(i_properties, ensure_ascii=False), i_is_virtual, i_parent,
                       i_parent, 0, i_img, i_comment, i_setting_time, i_expiration_time))
            new_id = c.lastrowid  # 并发时存在问题？我不知道
            if top_item is not None:  # 得保证容器内有东西
                top_item_id = top_item[0]
                c.execute('''UPDATE items SET sibling=? WHERE id=?''', (new_id, top_item_id))
    except sqlite3.Error as e:
        print('发生错误，原始日志：', e)
        return False, {'reason': 'exe failed', 'data': e}
    else:
        return True, new_id
    

def alter_item(i_id, i_name, i_class, i_properties, i_is_virtual, i_img, i_comment, i_expiration_time):  # 更新物品
    try:
        with conn:
            c = conn.cursor()
            c.execute('''UPDATE items SET name=?,class=?,properties=?,is_virtual=?,img=?,comment=?,expiration_time=? WHERE id=?''',
                      (i_name, i_class, json.dumps(i_properties, ensure_ascii=False), i_is_virtual, i_img, i_comment, i_expiration_time, i_id))
    except sqlite3.Error as e:
        return False, {'reason': 'exe failed', 'data': e}
    else:
        return True, ''


def move_item(i_id, now_parent, now_sibling, target_parent, target_sibling):  # 移动物品
    try:
        with conn:
            c = conn.cursor()
            # 移出的地方，更改链表关系
            c.execute('''SELECT id FROM items WHERE parent=? AND sibling=?''', (now_parent, i_id))
            target_pos_item = c.fetchone()
            if target_pos_item is not None:  # 保证能查到东西
                target_pos_item_id = target_pos_item[0]
                c.execute('''UPDATE items SET sibling=? WHERE id=?''', (now_sibling, target_pos_item_id))
            # 插入的地方，更改链表关系
            c.execute('''SELECT id FROM items WHERE parent=? AND sibling=?''', (target_parent, target_sibling))
            target_pos_item = c.fetchone()
            if target_pos_item is not None:  # 保证能查到东西
                target_pos_item_id = target_pos_item[0]
                c.execute('''UPDATE items SET sibling=? WHERE id=?''', (i_id, target_pos_item_id))
            # 插入
            c.execute('''UPDATE items 
                                SET parent=?, previous_parent=?, sibling=? 
                                WHERE id=?''', (target_parent, now_parent, target_sibling, i_id))
    except sqlite3.Error as e:
        print('move_item发生错误，原始日志：', e)
        return False
    else:
        return True


def get_children(parent):  # 给定parent，获取其子，返回结果按照从栈顶到栈底排列
    c = conn.cursor()
    c.execute('''SELECT id,name,sibling,img
                FROM items WHERE parent=?''', (parent, ))
    result = c.fetchall()
    ret = []
    now_target = 0  # 从栈顶开始查
    while len(result):
        for i in result:
            if i[2] == now_target:  # sibling
                ret.append({
                    'id': i[0],
                    'name': i[1],
                    'sibling': i[2],
                    'img': i[3]
                })
                now_target = i[0]  # id
                result.remove(i)
                break
    return ret


def del_item(i_id):  # 删除元素
    with conn:
        c = conn.cursor()
        item_info = get_item(i_id)
        if item_info is None:
            return False, {'reason': 'no id info'}
        else:
            # 找一下我是谁哥哥
            c.execute('''SELECT id FROM items WHERE sibling=?''', (i_id, ))  # sibling的id是唯一的（除了0，但这里不出现）
            result = c.fetchone()
            if result is not None:  # 保证能查到东西
                c.execute('''UPDATE items SET sibling=? WHERE id=?''', (item_info['sibling'], result[0]))
            wait_for_del = [i_id]  # 待删除栈
            del_info = []
            while len(wait_for_del) != 0:
                del_id = wait_for_del.pop()
                del_item_info = get_item(del_id)  # 虽然重复了，但为了循环结构简单，问题不大。
                c.execute('''DELETE FROM items WHERE id=?''', (del_id, ))
                del_info.append(del_item_info)
                thumbnail_name = del_item_info['img']
                if thumbnail_name != '':
                    image_path = os.path.abspath(os.path.join(config.PIC_PATH,  thumbnail_name.replace('_sm', '')))
                    thumbnail_path = os.path.abspath(os.path.join(config.PIC_PATH,  thumbnail_name))
                    os.remove(image_path)
                    os.remove(thumbnail_path)
                # 递归查找删除目标
                children = get_children(del_id)
                for children_info in children:
                    wait_for_del.append(children_info['id'])
            return True, del_info