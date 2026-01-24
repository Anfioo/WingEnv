from rich.console import Console

console = Console()

# 使用标记语言设置样式
console.print("Hello [bold red]World[/bold red]!", ":vampire:")
console.print("这是一段 [underline cyan]下划线加青色[/underline cyan] 的文字。")
console.print("[strike]删除线文字[/strike]", style="green on white")