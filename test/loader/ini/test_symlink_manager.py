from loader.envs_enum import EnvsEnum
from loader.ini.symlink_manager import EnvsSymlinkManager

manager = EnvsSymlinkManager()
manager.add_symlink(EnvsEnum.JDK, r"C:\Envs\JDK\jdk-17.0.12", "dir", "backup")
# manager.remove_symlink("jdk")

print(manager.get_symlink(EnvsEnum.JDK))
