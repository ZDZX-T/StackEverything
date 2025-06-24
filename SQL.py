import sqlite3
import os
import config
import datetime
from SQLs.items import *
from SQLs.classes import *
from SQLs.properties import *
from SQLs.connection import conn


def set_up_db():  # 尝试在表格未创建的情况下创建表格
    with conn:
        c = conn.cursor()
        # 检查是否需要新建
        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
        exists = c.fetchone() is not None
        if not exists:
            print('创建数据库')
            # 创建class表
            c.execute('''CREATE TABLE classes (
                class TEXT PRIMARY KEY, -- 主键
                rank INTEGER            -- 排名或等级，整数类型
            )''')
            # 创建items表
            c.execute('''CREATE TABLE items (
                id INTEGER PRIMARY KEY,          -- 主键，自动递增
                name TEXT NOT NULL,              -- 名称，文本类型，不允许为空
                class TEXT,                      -- 分类，文本类型
                properties TEXT,                 -- 属性，文本类型
                is_virtual INTEGER CHECK (is_virtual IN (0, 1)),  -- 布尔值，用整数表示
                parent INTEGER,                  -- 父节点ID，整数类型
                previous_parent INTEGER,         -- 之前的父节点ID
                sibling INTEGER,                 -- 兄弟节点ID，整数类型
                img TEXT,                        -- 图片路径或URL，文本类型
                comment TEXT,                    -- 备注，文本类型
                setting_time TEXT,               -- 入库时间，YYYY-MM-DD HH:MM:SS
                expiration_time TEXT,            -- 保质期，YYYY-MM-DD
                FOREIGN KEY(class) REFERENCES classes(class)   -- 设置外键约束
            )''')
            # 创建文件夹
            try:
                os.mkdir(config.PIC_PATH)
            except FileExistsError:
                pass  # 文件夹已经存在，用就完事了，当做无事发生
            # 创建property表
            c.execute('''CREATE TABLE properties (
                class TEXT,                    -- 分类，文本类型
                property TEXT,                 -- 属性名称，文本类型
                form TEXT,                     -- 形式，文本类型
                range TEXT,                    -- 范围，文本类型
                rank INTEGER,                  -- 排名或等级，整数类型
                comment TEXT,                  -- 备注，文本类型
                PRIMARY KEY (class, property), -- 设置复合主键
                FOREIGN KEY (class) REFERENCES classes(class) -- 设置外键约束
                    ON DELETE CASCADE -- 设置级联删除
            )''')
            c.execute('PRAGMA user_version = 1')  # 设置数据库版本号
            conn.commit()
            print('数据库创建完毕')
            new_class('区域')
            new_item('公共区', '区域', {}, True, 0, '', '公共区域，物品从存储地点取出后会移动到这里', '')


set_up_db()

if __name__ == '__main__':
    # new_item('test', '测试物品', '', False, 1, '', '插入物品')
    # new_item('test1', '测试物品', '', False, 1, '', '插入物品')
    # print(get_children(0))
    # print(get_children(1))
    # move_item(2, 1, 3, 1, 0)
    # print(get_classes())
    # new_class('test1')
    # new_class('test2')
    # new_class('test3')
    # new_class('test4')
    # print(manage_all_class(['test1', 'test2', 'test4']))
    # print(get_properties())
    # print(get_properties_info('衣物'))
    print(get_available_item_name('测试'))
    pass
