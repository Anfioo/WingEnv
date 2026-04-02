from dataclasses import dataclass

from loader import DownloadsManager
from loader.ini.extract_manager import ExtractManager
from loader.style_loader import StyleLoader

from wing_ui.dialog_ui import WingUI
from wing_ui.rich_wing_ui import RichWingUI
from wing_utils.extract import UniversalExtractor
from loader.ini.theme_manager import ThemeManager


@dataclass
class BaseInstallCLIData:
    tm: "ThemeManager"
    sl: "StyleLoader"
    downloadsManager: "DownloadsManager"
    extractManager: "ExtractManager"
    wingUi: "WingUI"
    universalExtractor: "UniversalExtractor"
    richUi: "RichWingUI"



