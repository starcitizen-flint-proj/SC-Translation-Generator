import os, re
import logging
import config

from io import TextIOWrapper

def read_file_lines(file: TextIOWrapper) -> list[str]:
    content = file.read().replace(config.UNKNOWN_CHR, config.REPLACE_CHR)
    lines = content.splitlines()
    return lines

class TextReader():
    
    def __init__(
        self,
        base_path: str = config.TEXT_FILE_DIR,
        en_file: str = config.EN_FILE_NAME,
        cn_file: str = config.CN_FILE_NAME
    ) -> None:
        self.id_set  = set()
        self.en_dict = dict()
        self.cn_dict = dict()
        with open(os.path.join(base_path, en_file), 'r', encoding=config.ENCODE, errors='replace') as file:
            logging.info(f"Reading {os.path.join(base_path, en_file)}")
            for line in read_file_lines(file):
                tid, _, text = line.partition('=')
                self.id_set.add(tid)
                self.en_dict[tid] = text
        with open(os.path.join(base_path, cn_file), 'r', encoding=config.ENCODE, errors='replace') as file:
            logging.info(f"Reading {os.path.join(base_path, cn_file)}")
            for line in read_file_lines(file):
                tid, _, text = line.partition('=')
                self.id_set.add(tid)
                self.cn_dict[tid] = text
    
    def get(self, tid):
        if tid not in self.id_set: return None
        return {
            'en': self.en_dict.get(tid),
            'cn': self.cn_dict.get(tid)
        }
    
    def find_ids_by_pattern(self, pattern: str | re.Pattern[str]):
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        ids = [tid for tid in self.id_set if pattern.match(tid)]
        ret_data = dict()
        for tid in ids:
            ret_data[tid] = {
                'en': self.en_dict.get(tid),
                'cn': self.cn_dict.get(tid)
            }
        return ret_data
    
    
        