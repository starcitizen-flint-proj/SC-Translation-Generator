import re, json

class GenerationManager():
    
    def __init__(self, config_file_path):
        with open(config_file_path, 'r', encoding='utf-8') as config_file:
            self.config = json.load(config_file)
    
    def temp_rule_regex(self):
        pass