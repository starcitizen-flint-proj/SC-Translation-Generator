import os
import config
from generation_manager import GenerationManager
from cstone_ruleset import *
from local_ruleset import *

maker = GenerationManager(
    os.path.join(config.TEXT_FILE_DIR, 'en.ini'), 
    os.path.join(config.TEXT_FILE_DIR, 'cn.ini'), 
    os.path.join(config.TEXT_FILE_DIR, 'ref.ini')
)

maker.apply_rulesets([
    GeneralReplaceRuleset,
    CstoneFoodAndDrink,
    CstoneMissile,
    CstoneShipParts,
    BombRuleset
])

maker.generate(
    output_path=os.path.join(config.TEXT_FILE_DIR, 'output.ini'),
    suffix_data={'_starcitizen_doctor_localization_version': f"{maker.get_text('_starcitizen_doctor_localization_version')}_ZapAug"}
)