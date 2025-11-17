from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseRuleset(ABC):
    
    def __init__(self) -> None: 
        self.id_set = set()
    
    def get_ids(self) -> set[str]:
        return self.id_set
    
    @abstractmethod
    def translate(self, tid: str, cn_str: str|None, en_str: str|None) -> str:
        pass