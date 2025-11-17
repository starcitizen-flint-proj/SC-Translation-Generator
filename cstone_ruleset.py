from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import requests
import time

class BaseCstoneTranslator(ABC):
    
    def __init__(
        self, 
        special_id_file, 
        replace_map_file, 
        ignore_id_file, 
        base_url: str = 'https://finder.cstone.space', 
        auto_grab = True
    ) -> None:
        
        self.base_url = base_url
        self.data = dict()
        self.id_set = set()
        
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
                
        if auto_grab:
            self.grab_data_batch()
        
    def call_api(self, api: str):
        api = api.removeprefix('/')
        base_url = self.base_url.removesuffix('/')
        now_timestamp = int(time.time() * 1000)
        response = requests.get(f"{base_url}/{api}?_={now_timestamp}")
        response.raise_for_status()
        return response.json()
        
    @abstractmethod
    def _grab_data(self, api: str) -> None:
        pass
    
    @abstractmethod
    def grab_data_batch(self) -> None:
        pass
    
    @abstractmethod
    def translate(self, tid: str, cn_str: str|None, en_str: str|None) -> str:
        pass
    
    def get_ids(self) -> set[str]:
        return self.id_set
    
class CstoneShipParts(BaseCstoneTranslator):
    
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
        
    def _grab_data(self, api: str):
        json_data = self.call_api(api)
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
                'class': self.__replace(d['ItemClass']),    # 军/民/工, etc
                'grade': d['Grade'],                        # A/B/C/D
                'type': self.__replace(d['Type']),          # 冷却/发电, etc
            }
            self.id_set.add(tids)
            
    def grab_data_batch(self) -> None:
        for api in self.APIS:
            self._grab_data(api)
            
    def __replace(self, name):
        return self.replace_map.get(name, name)
    
    def translate(self, tid: str|tuple, cn_str: str|None, en_str: str|None) -> str:
        if cn_str is None or en_str is None: raise RuntimeError("文本未提供")
        stat = self.data[tid]
        return f"{en_str} [S{stat['size']}{stat['class']}{stat['grade']} {cn_str}]({stat['type']})"
    
class CstoneFoodAndDrink(BaseCstoneTranslator):
    
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
        
    def _grab_data(self, api: str):
        json_data = self.call_api(api)
        for d in json_data:
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
            if int(d['Hunger']) == 0 and int(d['Thirst']) == 0: 
                # 包括了一些没效果的东西，忽略掉
                continue
            self.data[tids] = {
                'hunger': int(d['Hunger']), # 饥饿度
                'thirst': int(d['Thirst']), # 口渴度
            }
            self.id_set.add(tids)
            
    def grab_data_batch(self) -> None:
        for api in self.APIS:
            self._grab_data(api)
    
    def translate(self, tid: str|tuple, cn_str: str|None, en_str: str|None) -> str:
        if cn_str is None or en_str is None: raise RuntimeError("文本未提供")
        stat = self.data[tid]
        return f"{en_str}\\n{cn_str} NDR:{stat['hunger']} HEI:{stat['thirst']}"