# 向所有json新增字段
import json

files = ['zh-cn.json', 'en.json']
datas = {}
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        datas[file] = json.load(f)

while 1:
    key = input("请输入键（输入 0 停止）：")
    if key == '0':
        break
    if key in datas[files[0]].keys():  # 重复了
        print('key已存在，请更改后重新录入key')
        continue
    for target in files:
        value = input(f'{target}:')
        datas[target][key] = value

for file in files:
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(datas[file], f, indent=4, ensure_ascii=False)