#!/usr/bin/env python
from prompt_toolkit.shortcuts import radiolist_dialog

from wing_env_install.java_install.single_java_install import  java_install


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
            java_install()


if __name__ == "__main__":
    select_env()
