from pathlib import Path
from typing import Optional, Dict

from conf.STYLE_CONFIG import STYLE_CONFIG
from install.client.ini.base_install_ini_manager import BaseInstallIniManager
from loader import EnvsSymlinkManager
from loader.envs_enum import EnvsEnum
from wing_utils import IniConfigUtils
from wing_utils.common.gzip_utils import GzipUtils


class JdksManager(BaseInstallIniManager):
    def __init__(self):
        super().__init__(EnvsEnum.JDK)

