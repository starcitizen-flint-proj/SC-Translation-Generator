from generation_manager import GenerationManager
from cstone_ruleset import CstoneShipParts

VERSION = "4.3.2"

maker = GenerationManager(f"text_files\\{VERSION}\\en.ini", f"text_files\\{VERSION}\\cn.ini", f"text_files\\{VERSION}\\global.ini")

ship_parts_translator = CstoneShipParts()
maker.process(
    ids=ship_parts_translator.get_ids(), 
    translate=ship_parts_translator.translate
)

maker.generate(
    output_path=f"text_files\\{VERSION}\\output.ini",
    suffix_data={'_starcitizen_doctor_localization_version': f"{maker.get_text('_starcitizen_doctor_localization_version')}_ZapAug"}
)