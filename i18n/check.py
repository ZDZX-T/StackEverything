# 用来检查其他json的字段是否与zh-cn.json字段相同
import json
import os

base_file_name = 'zh-cn.json'
target_files = ['en.json']

with open(base_file_name, 'r', encoding='utf-8') as f:
    base_json = json.load(f)

for target in target_files:
    print(f'正在检查{target}')
    if not os.path.exists(target):
        with open(target, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
    with open(target, 'r', encoding='utf-8') as f:
        target_json = json.load(f)
    changed = False
    save_json = {}  # 不断添加，保证次序相同
    for key in base_json.keys():
        if key not in target_json:
            save_json[key] = input(f'缺失【{key}】,原文【{base_json[key]}】,译文:')
            changed = True
        else:
            save_json[key] = target_json[key]
    if changed:
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(save_json, f, indent=4, ensure_ascii=False)

print('全部检查完毕')