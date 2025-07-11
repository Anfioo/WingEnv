from wing_ui.edit_ui import TextEditorApp

if __name__ == "__main__":
    # 自动打开指定文件，如果没有传参数则为空编辑器
    editor = TextEditorApp(r"C:\Apps\Envs\Demo\apache-maven-3.9.10\conf\settings.xml")  # 或 path=None
    editor.run()
