import os, re

def split_by_first_equal(text):
    if '=' in text:
        parts = text.split('=', 1)  # 只分割第一个等号
        return parts[0], parts[1]
    else:
        return None, None  # 如果没有等号，返回None
        
# 读取文件
files = dict()
for file in os.listdir('text_files'):
    files[file.replace('.ini', '')] = dict()
    with open(os.path.join('text_files', file), 'r', encoding='utf-8') as fp:
        for line in fp.readlines():
            id, text = split_by_first_equal(line)
            if text[-1] == '\n':
                text = text[:-1]
            files[file.replace('.ini', '')][id] = text

# 暂时按照固定规则处理
result = dict()
ids = files['2lang_official'].keys()
used = set()
for id in ids:
    groups = re.match(r'RR_([A-Z]{3})_(L\d)', id)
    if groups and (not re.match(r'.*_desc.*', id)) and (not re.match(r'.*_Desc.*', id)):
        result[id] = f'{groups[1]}-{groups[2]} [{files["zh"][id]}]'
        used.add(id)
    if re.match(r'FOB_.*_FOB', id) and (not re.match(r'.*_desc.*', id)) and (not re.match(r'.*_Desc.*', id)):
        result[id] = f'{files["en"][id]} - [{files["zh"][id]}]'
        used.add(id)

for id in ids:
    if id in used:
        continue
    else:
        if id in files['2lang_official'].keys():
            result[id] = files['2lang_official'][id]
        else:
            result[id] = files['en'][id]

with open('global.ini', 'w', encoding='utf-8') as fp:
    for id in ids:
        # print(result[id])
        fp.write(f'{id}={result[id]}\n')
        pass