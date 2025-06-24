import json
import sys
sys.path.insert(0, '../../')
from config import LANGUAGE

i18n = {}
with open(f'i18n/{LANGUAGE}.json', 'r', encoding='utf-8') as f:  # 不知道为什么这里的文件路径只能这样写。。
    i18n = json.load(f)
