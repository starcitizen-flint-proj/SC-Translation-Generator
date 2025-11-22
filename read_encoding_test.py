import os
import chardet
import config

for filename in os.listdir(config.TEXT_FILE_DIR):
    if not filename.endswith('.ini'): continue
    # 先检测文件编码
    with open(os.path.join(config.TEXT_FILE_DIR, filename), 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        print(f"{f} 检测到的编码: {encoding}")