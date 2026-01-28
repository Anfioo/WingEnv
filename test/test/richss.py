import time
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.spinner import Spinner

console = Console()

SPINNERS = [
    "dots", "dots2", "dots3", "dots4", "dots5", "dots6", "dots7", "dots8",
    "line", "line2", "pipe",
    "simpleDots", "simpleDotsScrolling",
    "star", "star2", "flip", "hamburger",
    "growVertical", "growHorizontal",
    "balloon", "balloon2", "noise",
    "bounce", "boxBounce", "boxBounce2",
    "triangle", "arc", "circle",
    "squareCorners", "circleQuarters",
]


def build_table(spinner_objs, per_row=3):
    table = Table(
        title="Rich Spinner Gallery (3 per row)",
        show_header=True,
        header_style="bold #5ad12f",
        box=None,  # 更紧凑一点，也可以删掉
    )

    # 每个 spinner 占两列：动画 + 名称
    for i in range(per_row):
        table.add_column("Spinner", justify="center")
        table.add_column("Name", style="yellow")

    row = []
    count = 0

    for name, spinner in spinner_objs:
        row.append(spinner)
        row.append(name)
        count += 1

        if count == per_row:
            table.add_row(*row)
            row = []
            count = 0

    # 补齐最后一行
    if row:
        while len(row) < per_row * 2:
            row.append("")
        table.add_row(*row)

    return table


if __name__ == "__main__":
    spinner_objs = [
        (name, Spinner(name, style="bold cyan"))
        for name in SPINNERS
    ]

    with Live(
            build_table(spinner_objs),
            refresh_per_second=20,
            console=console,
    ) as live:
        start = time.time()
        while time.time() - start < 10:
            live.update(build_table(spinner_objs))
            time.sleep(0.05)
