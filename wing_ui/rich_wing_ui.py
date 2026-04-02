from typing import Dict, List, Optional, Union, Any
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich.columns import Columns
from rich.align import Align
from loader.style_loader import StyleLoader
from wing_utils.ui import console
import re


class RichWingUI:
    def __init__(self, styleLoader: StyleLoader):
        self.styleLoader = styleLoader
        self.console = console
        self._base_bg = "#fdf6ec"
        self._base_fg = "#3e2723"
        self._init_colors()

    def yes_or_no(
            self,
            prompt: str = "是否继续？",
            default_yes: bool = True
    ) -> bool:
        """
        Rich 官方确认框（是/否）
        完全不使用原生 input，光标永远不会偏移/上跳
        """
        return Confirm.ask(
            prompt=f"[{self._get_label_color()}]{prompt}[/{self._get_label_color()}]",
            default=default_yes,
            console=self.console
        )

    def flash(self):
        self.styleLoader.flash()
        self._init_colors()

    def get_style_loader(self):
        return self.styleLoader

    def _init_colors(self):
        dialog_style = self._get_color("dialog", "bg:#fdf6ec fg:#3e2723")
        self._base_bg = self._extract_color(dialog_style, "bg")
        self._base_fg = self._extract_color(dialog_style, "fg")

    def _get_color(self, key: str, default: str = "white") -> str:
        try:
            style_dict = self.styleLoader.style_dict
            return style_dict.get(key, default)
        except:
            return default

    def _extract_color(self, style_string: str, color_type: str = "bg") -> str:
        try:
            parts = style_string.split()
            for part in parts:
                if part.startswith(f"{color_type}:"):
                    return part.split(":")[1].strip()
            return "white"
        except:
            return "white"

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb: tuple) -> str:
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    def _adjust_brightness(self, hex_color: str, factor: float) -> str:
        rgb = self._hex_to_rgb(hex_color)
        new_rgb = tuple(min(255, max(0, int(c * factor))) for c in rgb)
        return self._rgb_to_hex(new_rgb)

    def _mix_with_white(self, hex_color: str, white_ratio: float = 0.3) -> str:
        rgb = self._hex_to_rgb(hex_color)
        white = (255, 255, 255)
        new_rgb = tuple(
            int(c * (1 - white_ratio) + w * white_ratio)
            for c, w in zip(rgb, white)
        )
        return self._rgb_to_hex(new_rgb)

    def _get_luminance(self, hex_color: str) -> float:
        rgb = self._hex_to_rgb(hex_color)
        return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255

    def _get_contrast_color(self, hex_color: str) -> str:
        rgb = self._hex_to_rgb(hex_color)
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        return "#000000" if luminance > 0.5 else "#ffffff"

    def _ensure_readable_fg(self, hex_color: str) -> str:
        luminance = self._get_luminance(hex_color)
        if luminance < 0.2:
            return self._mix_with_white(hex_color, 0.4)
        elif luminance < 0.3:
            return self._mix_with_white(hex_color, 0.25)
        elif luminance < 0.4:
            return self._mix_with_white(hex_color, 0.15)
        return hex_color

    def _get_dialog_bg(self) -> str:
        return self._base_bg

    def _get_dialog_fg(self) -> str:
        return self._ensure_readable_fg(self._base_fg)

    def _get_frame_border(self) -> str:
        return self._adjust_brightness(self._base_fg, 0.7)

    def _get_label_color(self) -> str:
        return self._ensure_readable_fg(self._adjust_brightness(self._base_fg, 1.3))

    def _get_text_color(self) -> str:
        return self._ensure_readable_fg(self._base_fg)

    def _get_button_color(self) -> str:
        return self._adjust_brightness(self._base_bg, 0.85)

    def _get_button_text_color(self) -> str:
        return self._ensure_readable_fg(self._base_fg)

    def _get_button_focused_color(self) -> str:
        return self._adjust_brightness(self._base_fg, 0.8)

    def _get_title_color(self) -> str:
        return self._ensure_readable_fg(self._adjust_brightness(self._base_fg, 1.4))

    def _get_header_color(self) -> str:
        return self._ensure_readable_fg(self._adjust_brightness(self._base_fg, 1.2))

    def print_dict_as_table(
            self,
            data: Dict[str, Any],
            title: Optional[str] = None,
            key_column: str = "键",
            value_column: str = "值",
            show_index: bool = False
    ):
        table = Table(
            title=title,
            show_header=True,
            header_style=f"bold {self._get_header_color()}",
            title_style=f"bold {self._get_title_color()}",
            border_style=self._get_frame_border()
        )

        if show_index:
            table.add_column("#", style="dim", width=3)
        table.add_column(key_column, style=self._get_label_color())
        table.add_column(value_column, style=self._get_text_color())

        for idx, (key, value) in enumerate(data.items(), 1):
            if show_index:
                table.add_row(str(idx), str(key), str(value))
            else:
                table.add_row(str(key), str(value))

        self.console.print(table)

    def print_list_as_table(
            self,
            data: List[Any],
            title: Optional[str] = None,
            column_name: str = "项目",
            show_index: bool = True
    ):
        table = Table(
            title=title,
            show_header=True,
            header_style=f"bold {self._get_header_color()}",
            title_style=f"bold {self._get_title_color()}",
            border_style=self._get_frame_border()
        )

        if show_index:
            table.add_column("#", style="dim", width=3)
        table.add_column(column_name, style=self._get_label_color())

        for idx, item in enumerate(data, 1):
            if show_index:
                table.add_row(str(idx), str(item))
            else:
                table.add_row(str(item))

        self.console.print(table)

    def print_table(
            self,
            data: Union[List[Dict[str, Any]], List[List[Any]]],
            columns: Optional[List[str]] = None,
            title: Optional[str] = None,
            show_index: bool = False
    ):
        table = Table(
            title=title,
            show_header=True,
            header_style=f"bold {self._get_header_color()}",
            title_style=f"bold {self._get_title_color()}",
            border_style=self._get_frame_border()
        )

        if show_index:
            table.add_column("#", style="dim", width=3)

        if isinstance(data[0], dict):
            if columns is None:
                columns = list(data[0].keys())
            for col in columns:
                table.add_column(col, style=self._get_label_color())
            for idx, row in enumerate(data, 1):
                values = [str(row.get(col, "")) for col in columns]
                if show_index:
                    table.add_row(str(idx), *values)
                else:
                    table.add_row(*values)
        else:
            if columns is None:
                columns = [f"列{i + 1}" for i in range(len(data[0]))]
            for col in columns:
                table.add_column(col, style=self._get_label_color())
            for idx, row in enumerate(data, 1):
                values = [str(cell) for cell in row]
                if show_index:
                    table.add_row(str(idx), *values)
                else:
                    table.add_row(*values)

        self.console.print(table)

    def print_panel(
            self,
            content: Union[str, Text, Table],
            title: Optional[str] = None,
            border_style: Optional[str] = None
    ):
        if border_style is None:
            border_style = self._get_frame_border()

        panel = Panel(
            content,
            title=title,
            border_style=border_style
        )
        self.console.print(panel)

    def print_tree(
            self,
            data: Dict[str, Any],
            title: Optional[str] = None
    ):
        if title:
            tree = Tree(f"[bold {self._get_label_color()}]{title}[/bold {self._get_label_color()}]")
        else:
            tree = Tree("根")

        def add_node(branch, key, value):
            if isinstance(value, dict):
                node = branch.add(f"[{self._get_label_color()}]{key}[/{self._get_label_color()}]")
                for k, v in value.items():
                    add_node(node, k, v)
            elif isinstance(value, (list, tuple)):
                node = branch.add(f"[{self._get_label_color()}]{key}[/{self._get_label_color()}]")
                for i, item in enumerate(value):
                    add_node(node, f"[{i}]", item)
            else:
                branch.add(
                    f"[{self._get_label_color()}]{key}[/{self._get_label_color()}]: [{self._get_text_color()}]{value}[/{self._get_text_color()}]")

        for key, value in data.items():
            add_node(tree, key, value)

        self.console.print(tree)

    def print_columns(
            self,
            items: List[Union[str, Text, Table, Panel]],
            title: Optional[str] = None,
            equal: bool = True,
            expand: bool = True
    ):
        columns = Columns(items, equal=equal, expand=expand)
        if title:
            self.console.print(f"[bold {self._get_title_color()}]{title}[/bold {self._get_title_color()}]")
        self.console.print(columns)

    def print_info(self, message: str, title: str = "信息"):
        text = Text(message, style=self._get_text_color())
        self.print_panel(text, title=title)

    def print_warning(self, message: str, title: str = "警告"):
        text = Text(message, style="bold yellow")
        self.print_panel(text, title=title, border_style="yellow")

    def print_error(self, message: str, title: str = "错误"):
        text = Text(message, style="bold red")
        self.print_panel(text, title=title, border_style="red")

    def print_success(self, message: str, title: str = "成功"):
        text = Text(message, style="bold green")
        self.print_panel(text, title=title, border_style="green")

    def print_list(
            self,
            items: List[Any],
            title: Optional[str] = None,
            numbered: bool = True,
            bullet: str = "•"
    ):
        if title:
            self.console.print(f"[bold {self._get_title_color()}]{title}[/bold {self._get_title_color()}]")

        for idx, item in enumerate(items, 1):
            if numbered:
                self.console.print(
                    f"[{self._get_label_color()}]{idx}.[/{self._get_label_color()}] [{self._get_text_color()}]{item}[/{self._get_text_color()}]")
            else:
                self.console.print(
                    f"[{self._get_label_color()}]{bullet}[/{self._get_label_color()}] [{self._get_text_color()}]{item}[/{self._get_text_color()}]")

    def print_key_value(
            self,
            data: Dict[str, Any],
            title: Optional[str] = None,
            separator: str = ": "
    ):
        if title:
            self.console.print(f"[bold {self._get_title_color()}]{title}[/bold {self._get_title_color()}]")

        for key, value in data.items():
            self.console.print(
                f"[{self._get_label_color()}]{key}[/{self._get_label_color()}]{separator}[{self._get_text_color()}]{value}[/{self._get_text_color()}]")

    def print_aligned(
            self,
            text: str,
            align: str = "center",
            style: Optional[str] = None
    ):
        if style is None:
            style = self._get_text_color()

        text_obj = Text(text, style=style)
        if align == "center":
            aligned = Align.center(text_obj)
        elif align == "left":
            aligned = Align.left(text_obj)
        elif align == "right":
            aligned = Align.right(text_obj)
        else:
            aligned = text_obj

        self.console.print(aligned)

    def print_rule(self, title: Optional[str] = None, style: Optional[str] = None):
        if style is None:
            style = self._get_frame_border()

        from rich.rule import Rule
        rule = Rule(title=title, style=style)
        self.console.print(rule)

    def clear(self):
        self.console.clear()


