from base_ruleset import BaseRuleset
import config
from utils import read_file_lines

class BombRuleset(BaseRuleset):
    
    """
    TODO
    临时的炸弹规则集
    """
    
    """
    item_NameBOMB_S03_FSKI_Thunderball=雷霆万钧 炸弹\nThunderball Bomb\n【S3 总伤27,000】
    item_NameBOMB_S05_FSKI_Stormburst=风爆 炸弹\nStormburst Bomb\n【S5 总伤46,702】
    item_NameBOMB_S10_FSKI_Colossus=巨像 炸弹\nColossus Bomb\n【S10 总伤568,297】
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.id_set = {
            'item_NameBOMB_S03_FSKI_Thunderball',
            'item_NameBOMB_S05_FSKI_Stormburst',
            'item_NameBOMB_S10_FSKI_Colossus'
        }
        self.stat = {
            'item_NameBOMB_S03_FSKI_Thunderball': (3, 27000),
            'item_NameBOMB_S05_FSKI_Stormburst': (5, 46702),
            'item_NameBOMB_S10_FSKI_Colossus': (10, 568297)
        }
        
    def translate(self, tid: str | tuple, cn_str: str | None, en_str: str | None) -> str:
        size, dmg = self.stat[str(tid)]
        return f"{en_str} [{cn_str}]\\nS{size} 伤害{dmg}"
    
class GeneralReplaceRuleset(BaseRuleset):
    
    """### 直接替换规则集  
    使用的ini文件和普通的文本文件基本一致  
    但是支持以`#`开头，不包括`=`的注释
    """
    
    def __init__(self, ruleset_folder = 'custom/data/direct_replace'):
        super().__init__()
        self.data = dict()
        import os, logging
        for filename in os.listdir(ruleset_folder):
            if (not filename.endswith('.ini')) or os.path.isdir(os.path.join(ruleset_folder, filename)): continue
            full_path = os.path.join(ruleset_folder, filename)
            logging.info(f"读取{full_path}")
            with open(full_path, 'r', encoding=config.ENCODE, errors='replace') as file:
                logging.info(f"Reading {full_path}")
                for line in read_file_lines(file):
                    tid, p, text = line.partition('=')
                    if (tid.startswith('#') or tid == '') and p != '=' and text == '':
                        continue
                    self.data[tid.upper()] = text
                    self.id_set.add(tid.upper())
                    
        logging.info('直接替换规则集初始化完毕')
    
    def translate(self, tid: str | tuple, cn_str: str | None, en_str: str | None) -> str:
        if isinstance(tid, tuple):
            tid = str(tid[0]).upper()
        if tid not in self.id_set: 
            raise KeyError('文本ID不存在')
        return self.data[tid]

# TODO
# class RepRuleset(BaseRuleset):
    
#     def __init__(self) -> None:
#         super().__init__()