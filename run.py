from generation_manager import GenerationManager
from cstone_ruleset import *
from local_ruleset import *

VERSION = '4.4.0'

maker = GenerationManager(
    f"text_files\\{VERSION}\\en.ini", 
    f"text_files\\{VERSION}\\cn.ini", 
    f"text_files\\{VERSION}\\global.ini"
)
maker.apply_rulesets([
    GeneralReplaceRuleset,
    CstoneFoodAndDrink,
    CstoneMissile,
    CstoneShipParts,
    BombRuleset
])

maker.generate(
    output_path=f"text_files\\{VERSION}\\output.ini",
    suffix_data={'_starcitizen_doctor_localization_version': f"{maker.get_text('_starcitizen_doctor_localization_version')}_ZapAug"}
)