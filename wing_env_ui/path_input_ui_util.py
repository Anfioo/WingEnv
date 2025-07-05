from prompt_toolkit.shortcuts import input_dialog


def input_install_path(default_path: str = "C:\\Apps\\Envs", title: str = "输入路径",
                       text: str = "请输入安装路径") -> str:
    """
    弹出输入框让用户输入 Java 安装路径

    Args:
        default_path (str): 默认路径（预填值）

    Returns:
        str: 用户输入的路径（若为空，则返回默认值）
        :param title:
        :param default_path:
        :param text:
    """
    result = input_dialog(
        title=title,
        text=text,
        default=default_path
    ).run()

    if result:
        return result.strip()
    else:
        return default_path

