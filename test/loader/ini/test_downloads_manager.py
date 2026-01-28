from loader.ini.downloads_manager import DownloadsManager
from loader.ini.symlink_manager import SymlinkManager

manager = DownloadsManager()
manager.add_download("graalvm-jdk-24.0.2_windows-x64_bin.zip.2",
                     r"C:\Apps\MyProjects\WingEnv\wing_utils\download\jdks\graalvm-jdk-24.0.2_windows-x64_bin.zip")
# manager.remove_symlink("jdk")

print(manager.list_downloads())

print(manager.get_download_path("graalvm-jdk-24.0.2_windows-x64_bin.zip"))
downloads_dir = manager.get_current_downloads_dir()
print(downloads_dir)
