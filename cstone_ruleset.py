import time, re
import requests
from abc import abstractmethod
from base_ruleset import BaseRuleset

class CstoneBaseRuleset(BaseRuleset):
    
    def __init__(
        self, 
        special_id_file, 
        replace_map_file, 
        ignore_id_file, 
        base_url: str = 'https://finder.cstone.space', 
        auto_grab = True
    ) -> None:
        
        super().__init__()
        
        self.base_url = base_url
        self.data = dict()
        self.apis = list()
        
        self.special_id_map = dict()
        self.replace_map    = dict()
        self.ignore_ids     = set()
        with open(special_id_file, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                target, _, tid = line.partition('=')
                tid = tid.removesuffix('\n')
                self.special_id_map[target] = tid
        with open(replace_map_file, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                src, _, dst = line.partition('=')
                dst = dst.removesuffix('\n')
                self.replace_map[src] = dst
        with open(ignore_id_file, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                tid = line.removesuffix('\n')
                self.ignore_ids.add(tid)
    
    def _replace(self, name):
        return self.replace_map.get(name, name)
        
    def _call_api(self, api: str):
        api = api.removeprefix('/')
        base_url = self.base_url.removesuffix('/')
        now_timestamp = int(time.time() * 1000)
        response = requests.get(f"{base_url}/{api}?_={now_timestamp}")
        response.raise_for_status()
        return response.json()
    
    # Cstone数据的规则集新增的需要实现的接口
    # 对某个API抓取数据
    @abstractmethod
    def _grab_data(self, api: str) -> None:
        pass
    
    def grab_data_batch(self) -> None:
        for api in self.apis:
            self._grab_data(api)

# NOTE 基础类，根据这个进行修改

class CstoneChangeMe(CstoneBaseRuleset):
    
    PREFIX_NAME = 'ITEM_NAME'
    APIS = ['',] 
    
    def __init__(
        self, 
        special_id_file     = 'custom/direct_id/CHANGEME.txt',
        replace_map_file    = 'custom/replace_map/CHANGEME.txt',
        ignore_id_file      = 'custom/ignore/CHANGEME.txt',
        base_url: str       = 'https://finder.cstone.space', 
        auto_grab = True, 
    ) -> None:
        super().__init__(special_id_file, replace_map_file, ignore_id_file, base_url, auto_grab)
        self.apis = self.APIS
        if auto_grab:
            self.grab_data_batch()
        
    def _grab_data(self, api: str):
        json_data = self._call_api(api)
        for d in json_data:
            # 获取基础ID
            base_id = str(d['ItemCodeName']).upper()
            if base_id in self.ignore_ids: continue
            # 处理ID生成可能的ID集合
            tids = (self.special_id_map.get(base_id),)
            tids = (
                f"{self.PREFIX_NAME}{base_id}",
            ) if tids[0] is None else tids
            # 收集需要的数据
            self.data[tids] = {
                
            }
            self.id_set.add(tids)
    
    def translate(self, tid: str|tuple, cn_str: str|None, en_str: str|None) -> str:
        if cn_str is None or en_str is None: raise RuntimeError("文本未提供")
        stat = self.data[tid]
        return f"{en_str} {cn_str}"

class CstoneMissile(CstoneBaseRuleset):
    
    PREFIX_NAME = 'ITEM_NAME'
    APIS = ['GetMissiles',] 
    
    def __init__(
        self, 
        special_id_file     = 'custom/direct_id/missile.txt',
        replace_map_file    = 'custom/replace_map/missile.txt',
        ignore_id_file      = 'custom/ignore/missile.txt',
        base_url: str       = 'https://finder.cstone.space', 
        auto_grab = True, 
    ) -> None:
        super().__init__(special_id_file, replace_map_file, ignore_id_file, base_url, auto_grab)
        self.apis = self.APIS
        if auto_grab:
            self.grab_data_batch()
        
    def _grab_data(self, api: str):
        json_data = self._call_api(api)
        for d in json_data:
            # 获取基础ID
            base_id = str(d['ItemCodeName']).upper()
            if base_id in self.ignore_ids: continue
            # 处理ID生成可能的ID集合
            tids = (self.special_id_map.get(base_id),)
            tids = (
                f"{self.PREFIX_NAME}{base_id}",
            ) if tids[0] is None else tids
            # 收集需要的数据
            self.data[tids] = {
                'speed': self._format_int(int(d['LinearSpeed'])),
                'dmg': self._format_int(int(d['Misdmg'])),
                'size': (int(d['Size'])),
                'track': self._replace(d['TrackingSignalType']),
            }
            self.id_set.add(tids)
    
    def translate(self, tid: str|tuple, cn_str: str|None, en_str: str|None) -> str:
        if cn_str is None or en_str is None: raise RuntimeError("文本未提供")
        stat = self.data[tid]
        return f"{en_str}\\n{cn_str}\\n[S{stat['size']}{stat['track']} 伤害{stat['dmg']} 速度{stat['speed']}]"

class CstoneShipParts(CstoneBaseRuleset):
    
    PREFIX_ITEM_NAME = 'ITEM_NAME'
    # NOTE 跳跃模块和刀片的名称/数据不对，这俩目前也没啥需要改的所以无所谓了
    APIS = ['GetCoolers', 'GetPowers', 'GetDrives', 'GetShields'] 
    
    def __init__(
        self, 
        special_id_file     = 'custom/direct_id/ship_parts.txt',
        replace_map_file    = 'custom/replace_map/ship_parts.txt',
        ignore_id_file      = 'custom/ignore/ship_parts.txt',
        base_url: str       = 'https://finder.cstone.space', 
        auto_grab = True, 
    ) -> None:
        super().__init__(special_id_file, replace_map_file, ignore_id_file, base_url, auto_grab)
        self.apis = self.APIS
        if auto_grab:
            self.grab_data_batch()
        
    def _grab_data(self, api: str):
        json_data = self._call_api(api)
        for d in json_data:
            base_id = str(d['ItemCodeName']).upper().removesuffix('SCITEM').removesuffix('_')
            if base_id in self.ignore_ids: continue
            tids = (self.special_id_map.get(base_id),)
            tids = (
                f"{self.PREFIX_ITEM_NAME}{base_id}",
                f"{self.PREFIX_ITEM_NAME}_{base_id}",
                f"{self.PREFIX_ITEM_NAME}{base_id}_SCITEM",
                f"{self.PREFIX_ITEM_NAME}_{base_id}_SCITEM",
            ) if tids[0] is None else tids
            self.data[tids] = {
                'size': d['Size'],                          # S1/2/3/4
                'class': self._replace(d['ItemClass']),    # 军/民/工, etc
                'grade': d['Grade'],                        # A/B/C/D
                'type': self._replace(d['Type']),          # 冷却/发电, etc
            }
            self.id_set.add(tids)
    
    def translate(self, tid: str|tuple, cn_str: str|None, en_str: str|None) -> str:
        if cn_str is None or en_str is None: raise RuntimeError("文本未提供")
        stat = self.data[tid]
        return f"{en_str} [S{stat['size']}{stat['class']}{stat['grade']} {cn_str}]({stat['type']})"
    
class CstoneFoodAndDrink(CstoneBaseRuleset):
    
    # TODO 添加食物效果
    
    PREFIX_NAME = 'ITEM_NAME'
    PREFIX_COMMODITIES = 'items_commodities'
    APIS = ['GetFoods', 'GetDrinks'] 
    
    def __init__(
        self, 
        special_id_file     = 'custom/direct_id/food_and_drink.txt',
        replace_map_file    = 'custom/replace_map/food_and_drink.txt',
        ignore_id_file      = 'custom/ignore/food_and_drink.txt',
        base_url: str       = 'https://finder.cstone.space', 
        auto_grab = True, 
    ) -> None:
        super().__init__(special_id_file, replace_map_file, ignore_id_file, base_url, auto_grab)
        self.apis = self.APIS
        if auto_grab:
            self.grab_data_batch()
        
    def _grab_data(self, api: str):
        json_data = self._call_api(api)
        for d in json_data:
            effect_result = re.search(r'Effect.*: *(.*?) *\\n', str(d['Desc']))
            effects = [self._replace(e) for e in effect_result.groups()[0].split(', ') if e != 'None'] if effect_result else []
            if int(d['Hunger']) == 0 and int(d['Thirst']) == 0 and len(effects) == 0: 
                # 包括了一些没效果的东西，忽略掉
                continue
            
            base_id = str(d['ItemCodeName']).upper().removesuffix('SCITEM').removesuffix('_')
            if base_id in self.ignore_ids: continue
            tids = (self.special_id_map.get(base_id),)
            tids = (
                f"{self.PREFIX_NAME}{base_id}",
                f"{self.PREFIX_NAME}_{base_id}",
                f"{self.PREFIX_NAME}{base_id}_SCITEM",
                f"{self.PREFIX_NAME}_{base_id}_SCITEM",
                f"{self.PREFIX_COMMODITIES}{base_id}",
                f"{self.PREFIX_COMMODITIES}_{base_id}",
                f"{self.PREFIX_COMMODITIES}{base_id}_SCITEM",
                f"{self.PREFIX_COMMODITIES}_{base_id}_SCITEM",
            ) if tids[0] is None else tids
            if base_id.startswith('HARVESTABLE_'):
                short_id = base_id.removeprefix('HARVESTABLE_')
                tids = list(tids)
                tids += [
                    f"{self.PREFIX_NAME}{short_id}",
                    f"{self.PREFIX_NAME}_{short_id}",
                    f"{self.PREFIX_NAME}{short_id}_SCITEM",
                    f"{self.PREFIX_NAME}_{short_id}_SCITEM",
                    f"{self.PREFIX_COMMODITIES}{short_id}",
                    f"{self.PREFIX_COMMODITIES}_{short_id}",
                    f"{self.PREFIX_COMMODITIES}{short_id}_SCITEM",
                    f"{self.PREFIX_COMMODITIES}_{short_id}_SCITEM",
                ]
                tids = tuple(tids)
            
            self.data[tids] = {
                'hunger': int(d['Hunger']), # 饥饿度
                'thirst': int(d['Thirst']), # 口渴度
                'effects': effects # 效果
            }
            self.id_set.add(tids)
    
    def translate(self, tid: str|tuple, cn_str: str|None, en_str: str|None) -> str:
        if cn_str is None or en_str is None: raise RuntimeError("文本未提供")
        stat = self.data[tid]
        result_str = f"{en_str} {cn_str}"
        
        if stat['hunger'] and stat['thirst']:
            result_str += f"\\nNDR:{stat['hunger']} HEI:{stat['thirst']}"
        elif stat['hunger']:
            result_str += f"\\nNDR:{stat['hunger']}"
        elif stat['thirst']:
            result_str += f"\\nHEI:{stat['thirst']}"
        
        if len(stat['effects']):
            result_str += ' ' if stat['hunger'] or stat['thirst'] else '\\n'
            result_str += ', '.join(stat['effects'])
            
        return result_str
