#!/usr/bin/env python
from prompt_toolkit.shortcuts import radiolist_dialog

from wing_env_install.java_install.multiple_java_install import java_multi_install
from wing_env_install.java_install.single_java_install import  single_java_install
from wing_env_ui.sure_ui_util import confirm_action_ui, show_message_ui


def select_env():
    result = radiolist_dialog(
        title="Select Environment",
        text="Which environment do you want to install?",
        values=[
            ("java", "Java"),
            ("nodejs-未开发", "Node.js-未开发"),
            ("go-未开发", "Go-未开发"),
            ("python-未开发", "Python-未开发"),
            ("rust-未开发", "Rust-未开发"),
        ],
    ).run()

    if result is None:
        print("No environment selected.")

    else:

        print(f"You selected: {result}")
        if result == "java":
            if confirm_action_ui("JAVA安装方式选择", "是否多版本JAVA安装？"):
                java_multi_install()
            else:
                single_java_install()



if __name__ == "__main__":
    select_env()
