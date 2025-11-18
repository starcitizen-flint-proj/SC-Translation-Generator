from base_ruleset import BaseRuleset

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