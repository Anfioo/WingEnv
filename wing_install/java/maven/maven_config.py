
from utils.file_utils import read_file_to_string, write_string_to_file
from utils.str_utils import StrManipulator, get_diff_blocks_with_line_numbers
import shutil
from utils.str_utils import StrManipulator
from wing_ui.edit_ui import TextEditorApp
from wing_ui.input_dialogs import input_text_ui
from wing_ui.sure_dialogs import yes_no_ui
from wing_ui.text_diff_viewer_ui import TextDiffViewerApp


def patch_maven_settings(file_path: str, local_repo_path: str):
    """
    修改 Maven 的 settings.xml 文件，添加 mirror 和本地仓库配置，同时备份原文件。

    :param file_path: 原始 Maven settings.xml 路径
    :param local_repo_path: 本地仓库路径，例如 C:/Apps/Envs/Maven/repository
    """
    # Step 1: 读取原始内容
    original_content = read_file_to_string(file_path)

    # Step 2: 替换 <mirrors> 块内容
    mirror_block = """
        <mirror>
            <id>nexus-aliyun</id>
            <mirrorOf>central</mirrorOf>
            <name>Nexus aliyun</name>
            <url>http://maven.aliyun.com/nexus/content/groups/public</url>      
        </mirror>

        <mirror>
            <id>maven-default-http-blocker</id>
            <mirrorOf>external:http:*</mirrorOf>
            <name>Pseudo repository to mirror external repositories initially using HTTP.</name>
            <url>http://0.0.0.0/</url>
            <blocked>true</blocked>
        </mirror>
    """
    updated_content = StrManipulator.replace_between(original_content, '<mirrors>', '</mirrors>', mirror_block)

    # Step 3: 插入 <localRepository>
    updated_content = StrManipulator.insert_after(
        updated_content,
        'xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.2.0 https://maven.apache.org/xsd/settings-1.2.0.xsd">'
        , f"\n<localRepository>{local_repo_path}</localRepository>"
    )
    print("已经帮你配置仓库路径为"+local_repo_path)
    print("已经帮你配置了镜像源 aliyun")


    # Step 4: 备份原文件
    backup_path = file_path + ".bak"
    shutil.copyfile(file_path, backup_path)

    # Step 5: 写入新内容
    write_string_to_file(file_path, updated_content)

    # Step 6: 输出差异块（可选）
    diffs = get_diff_blocks_with_line_numbers(original_content, updated_content)

    ui = yes_no_ui("预览差异", "是否需要预览配置差异？", "是", "否")
    if ui:
        viewer = TextDiffViewerApp(original_content, updated_content, diffs)
        viewer.run()


def config_ui_main(path):
    local_repo = input_text_ui(
        title="Maven 仓库路径输入",
        text="请输入 Maven 仓库目录",
        default="C:\\Apps\\Envs\\Maven\\repository"
    )

    if not local_repo:
        print("⚠️ 用户取消路径输入。")
        return None
    patch_maven_settings(path, local_repo)

    if yes_no_ui("修改配置文件", "是否需要修改配置文件？", "是", "否"):
        editor = TextEditorApp(path)
        editor.run()

