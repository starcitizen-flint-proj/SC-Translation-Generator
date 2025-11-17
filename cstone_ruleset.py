from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import requests
import time

class BaseCstoneTranslator(ABC):
    
    def __init__(self, base_url: str = 'https://finder.cstone.space', auto_grab = True) -> None:
        self.base_url = base_url
        self.data = dict()
        self.id_set = set()
        
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
    def translate(self, tid: str, cn_str: str, en_str: str) -> str:
        pass
    
    def get_ids(self) -> set[str]:
        return self.id_set
    
class CstoneShipParts(BaseCstoneTranslator):
    
    PREFIX_ITEM_NAME = 'ITEM_NAME'
    # NOTE 跳跃模块和刀片的名称/数据不对，这俩目前也没啥需要改的所以无所谓了
    APIS = ['GetCoolers', 'GetPowers', 'GetDrives', 'GetShields'] 
    NAME_TABLE = {
        'Civilian':     '民',
        'Civilian ':    '民',
        'Civilian  ':   '民',
        'Competition':  '竞',
        'Competition ': '竞',
        'Industrial':   '工',
        'Military':     '军',
        'Stealth':      '隐',
        'Stealth ':     '隐',
        'Cooler':       '冷却',
        'JumpDrive':    '跳跃模块',
        'PowerPlant':   '发电',
        'QuantumDrive': '量子',
        'Shield':       '护盾',
    }
    
    def __init__(self, base_url: str = 'https://finder.cstone.space', auto_grab = True, special_id_file = 'custom\direct_id\ship_parts.txt') -> None:
        super().__init__(base_url, auto_grab)
        self.special_replace_map = dict()
        with open(special_id_file, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                target, _, tid = line.partition('=')
                tid = tid.removesuffix('\n')
                self.special_replace_map[target] = tid
        if auto_grab:
            self.grab_data_batch()
        
    def _grab_data(self, api: str):
        json_data = self.call_api(api)
        for d in json_data:
            base_id = str(d['ItemCodeName']).upper().removesuffix('SCITEM').removesuffix('_')
            tids = (self.special_replace_map.get(base_id),)
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
        return self.NAME_TABLE.get(name, name)
    
    def translate(self, tid: str|tuple, cn_str: str, en_str: str) -> str:
        stat = self.data[tid]
        return f"{en_str} [S{stat['size']}{stat['class']}{stat['grade']} {cn_str}]({stat['type']})"