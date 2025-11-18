import re, json
import logging
from typing import Iterable, Callable
from typing import Type
from base_ruleset import BaseRuleset

class GenerationManager():
    
    def __init__(self, en_file, cn_file, ref_file) -> None:
        self.id_list = []
        self.id_map = dict()
        self.id_set = set()
        self.text_data = {
            'en': dict(),
            'cn': dict(),
            'ref': dict(),
        }
        file_map = {
            'en': en_file,
            'cn': cn_file,
            'ref': ref_file,
        }
        for key, filename in file_map.items():
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file.readlines():
                    tid, _, text = line.partition('=')
                    tid = tid.removeprefix('\ufeff')
                    text = text.removesuffix('\n')
                    self.text_data[key][tid] = text
                    if tid not in self.id_set:
                        self.id_list.append(tid)
                        self.id_set.add(tid)
                        self.id_map[tid.upper()] = tid

        self.processed = set()
        self.result_data = dict()
        
    def apply_single_ruleset(self, ruleset: BaseRuleset):
        self.process(ruleset.get_ids(), ruleset.translate)
            
    def apply_rulesets(self, rulesets: list[Type[BaseRuleset]]):
        for ruleset_cls in rulesets:
            logging.info(f"Applying ruleset {ruleset_cls.__name__}...")
            ruleset = ruleset_cls()
            self.apply_single_ruleset(ruleset)
            logging.info(f"Apply ruleset {ruleset_cls.__name__} finished.")
    
    def process(self, ids: Iterable[str], translate: Callable[[str|tuple, str|None, str|None], str]):
        for id in ids:
            tid = self.get_id(id)
            logging.info(tid)
            if tid not in self.id_set: 
                logging.warning(f"[PROC_MISSINGID] {tid}({id}) not found in id set")
                continue
            elif tid in self.processed:
                logging.info(f"{tid} processed, skip")
                continue
            try:
                self.result_data[tid] = translate(id, self.text_data['cn'][tid], self.text_data['en'][tid])
                logging.info(f"{id} -> {tid}: {self.result_data[tid]}")
                self.processed.add(id)
            except Exception as e:
                logging.warning(f"[PROC_EXECPTION] {e}")
                continue
            
    def generate(self, output_path, suffix_files: str|list|None = None, suffix_data: dict|None = None):
        with open(output_path, 'w', encoding='utf-8') as file:
            for id in self.id_list:
                tid = self.get_id(id)
                if tid is None:
                    logging.warning(f"[GEN_MISSINGID] {tid} not found in id set")
                    continue
                if tid in self.result_data.keys(): 
                    file.write(f"{tid}={self.result_data[tid]}\n")
                elif tid in self.text_data['ref'].keys():
                    file.write(f"{tid}={self.text_data['ref'][tid]}\n")
                else:
                    logging.warning(f"[GEN_MISSINGID] {tid} not found in result or reference")
            if suffix_files is not None:
                if isinstance(suffix_files, str):
                    suffix_files = [suffix_files]
                for suffix_file in suffix_files:
                    try:
                        with open(suffix_file, 'r', encoding='utf-8') as suffix:
                            file.write(suffix.read())
                    except Exception as e:
                        logging.warning(f"[GEN_EXECPTION] {e}")
            if suffix_data is not None:
                for tid, text in suffix_data.items():
                    file.write(f"{tid}={text}\n")

    def get_id(self, src_id: str|tuple) -> str|None:
        if isinstance(src_id, str):
            return self.id_map.get(src_id.upper())
        elif isinstance(src_id, tuple):
            for id in src_id:
                result = self.get_id(id)
                if result is not None: return result
        return None
    
    def get_text(self, tid: str, src: str = 'ref'):
        tid_s = self.get_id(tid)
        if tid_s is None:
            logging.warning(f"[GETTEXT_MISSINGID] {tid} not found")
            return self.text_data[src].get(tid)
        return self.text_data[src].get(tid_s)