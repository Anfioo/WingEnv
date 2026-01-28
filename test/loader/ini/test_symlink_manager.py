from loader.ini.symlink_manager import SymlinkManager

manager = SymlinkManager()
manager.add_symlink("jdk",r"C:\Envs\JDK\jdk-17.0.12","dir","backup")
# manager.remove_symlink("jdk")

print(manager.get_symlink("jdk"))
