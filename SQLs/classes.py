import sqlite3
from .connection import conn


def get_classes():  # 获取所有classes
    c = conn.cursor()
    # 执行查询
    c.execute("SELECT class FROM classes ORDER BY rank ASC")
    # 获取所有结果，并转换为列表
    result_list = [row[0] for row in c.fetchall()]
    return result_list


def check_class_name_exist(i_class):
    # 查看名称是否存在，存在返回true，不存在返回false
    c = conn.cursor()
    c.execute("SELECT class FROM classes WHERE class=?", (i_class,))
    row = c.fetchone()
    if row is not None:
        return True
    else:
        return False


def new_class(i_class):  # 新建class
    if check_class_name_exist(i_class):
        return False, {'reason': 'name exists'}
    try:
        with conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO classes (class, rank) VALUES (?, (SELECT COALESCE(MAX(rank), 0) + 1 FROM classes))",
                (i_class,)
            )
    except sqlite3.Error as e:
        print('new_class发生错误，原始日志：', e)
        return False, {'reason': 'exe failed', 'data': e}
    else:
        return True, ''


def manage_all_class(classes):  # 管理class，传入含所有class的列表（是数据库内数据的子集），将按照此去更新class表，包括删除和移动位置
    old_classes = get_classes()  # 首先获取现在的classes列表以作比较
    del_classes = [c for c in old_classes if c not in classes]  # 获取需要删除的class列表
    try:
        with conn:
            cursor = conn.cursor()
            cursor.executemany("DELETE FROM classes WHERE class=?", [(c,) for c in del_classes])  # 删除class
    except sqlite3.Error as e:
        print('manage_all_class发生错误，原始日志：', e)
        return False, {'reason': 'del error'}  # properties会被级联删除，items才会阻止
    try:
        with conn:
            cursor = conn.cursor()
            rank = 1
            for c in classes:
                cursor.execute("UPDATE classes SET rank=? WHERE class=?", (rank, c))
                rank += 1
    except sqlite3.Error as e:
        print('manage_all_class发生错误，原始日志：', e)
        return False, {'reason': 'rank error'}
    return True, ''
