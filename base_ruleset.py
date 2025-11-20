from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseRuleset(ABC):
    
    """
    基础规则集接口
    
    所有的规则集都需要在内部维护一个`id_set`(ID集合) 来指示这个规则集涉及哪些文本
    并实现`translate`翻译函数，接受id，中文原文，英文原文，返回生成的内容
    """
    
    def __init__(self) -> None: 
        self.id_set = set()
        
    def _format_int(self, num):
        return f"{num:,}"
    
    def get_ids(self) -> set[str]:
        return self.id_set
    
    @abstractmethod
    def translate(self, tid: str|tuple, cn_str: str|None, en_str: str|None) -> str:
        pass
    