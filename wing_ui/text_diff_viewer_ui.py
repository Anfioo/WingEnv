from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import VSplit, HSplit, Window, ConditionalContainer
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import WindowAlign
from prompt_toolkit.styles import Style, merge_styles
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.formatted_text import to_formatted_text

from typing import List, Tuple

from wing_utils.ui.diff_utils import DiffCalculator


class LineRangeHighlightLexer(Lexer):
    def __init__(self, highlight_ranges_with_styles: List[Tuple[Tuple[int, int], str]]):
        self.highlight_ranges_with_styles = highlight_ranges_with_styles

    def lex_document(self, document):
        def get_line(lineno):
            line_no_1based = lineno + 1
            for (start, end), style in self.highlight_ranges_with_styles:
                if start <= line_no_1based <= end:
                    text = document.lines[lineno]
                    return to_formatted_text([(style, text)])
            return to_formatted_text(document.lines[lineno])

        return get_line


class TextDiffViewerApp:
    class AppState:
        show_status_bar = True
        diff_index = 0

    def __init__(self, text1: str, text2: str,
                 diffs: List[Tuple[Tuple[int, int], Tuple[int, int]]]):
        self.AppState = TextDiffViewerApp.AppState
        self.diff_ranges = diffs or []

        styles = ['class:highlight1', 'class:highlight2', 'class:highlight3', 'class:highlight4']
        text1_ranges_with_styles = []
        text2_ranges_with_styles = []

        for i, ((start1, end1), (start2, end2)) in enumerate(self.diff_ranges):
            style = styles[i % len(styles)]
            text1_ranges_with_styles.append(((start1, end1), style))
            text2_ranges_with_styles.append(((start2, end2), style))

        self.text1_area = TextArea(
            text=text1,
            scrollbar=True,
            line_numbers=True,
            read_only=True,
            focusable=True,
            lexer=LineRangeHighlightLexer(text1_ranges_with_styles)
        )
        self.text2_area = TextArea(
            text=text2,
            scrollbar=True,
            line_numbers=True,
            read_only=True,
            focusable=True,
            lexer=LineRangeHighlightLexer(text2_ranges_with_styles)
        )

        self.kb = KeyBindings()
        self._register_key_bindings()

        self.body = HSplit([
            VSplit([
                self.text1_area,
                self.text2_area,
            ], padding=1),
            ConditionalContainer(
                content=VSplit([
                    Window(
                        FormattedTextControl(self._get_left_status),
                        style="class:status",
                    ),
                    Window(
                        FormattedTextControl(self._get_right_status),
                        style="class:status.right",
                        width=18,
                        align=WindowAlign.RIGHT,
                    ),
                ], height=2),
                filter=Condition(lambda: self.AppState.show_status_bar)
            )
        ])

        base_style = Style.from_dict({
            'status': 'reverse',
            'status.right': 'reverse',
            'highlight1': 'bg:#ff4444 #ffffff',
            'highlight2': 'bg:#44ff44 #000000',
            'highlight3': 'bg:#4444ff #ffffff',
            'highlight4': 'bg:#ffff44 #000000',
        })
        self.style = merge_styles([
            base_style,
            Style.from_dict({'highlight': 'bg:#4444ff #ffffff'})
        ])

        self.layout = Layout(self.body, focused_element=self.text1_area)

        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self.style,
            full_screen=True,
        )

    def _register_key_bindings(self):
        @self.kb.add("c-p")
        def _(event):  # Toggle status bar
            self.AppState.show_status_bar = not self.AppState.show_status_bar

        @self.kb.add("escape")
        def _(event):  # Exit app
            event.app.exit()

        @self.kb.add("c-n")
        def _(event):  # Next diff block
            if not self.diff_ranges:
                return
            self.AppState.diff_index = (self.AppState.diff_index + 1) % len(self.diff_ranges)
            self._goto_diff(self.AppState.diff_index)

        @self.kb.add(Keys.Tab)
        def _(event):  # Switch focus
            current_buffer = self.app.layout.current_control.buffer
            if current_buffer == self.text1_area.buffer:
                self.app.layout.focus(self.text2_area)
            else:
                self.app.layout.focus(self.text1_area)

    def _goto_diff(self, index: int):
        (start1, _), (start2, _) = self.diff_ranges[index]

        def safe_cursor(doc, line):
            line = max(0, min(line - 1, len(doc.lines) - 1))
            return doc.translate_row_col_to_index(line, 0)

        self.text1_area.buffer.cursor_position = safe_cursor(self.text1_area.document, start1)
        self.text2_area.buffer.cursor_position = safe_cursor(self.text2_area.document, start2)

    def _get_left_status(self):
        if self.diff_ranges:
            current = self.AppState.diff_index + 1
            total = len(self.diff_ranges)
            return f" 对比视图 | Ctrl-N 下一差异 [{current}/{total}] | Ctrl-P 状态栏 | Esc 退出 | Tab 切换焦点 "
        else:
            return " 对比视图 | Ctrl-P 状态栏 | Esc 退出 | Tab 切换焦点 "

    def _get_right_status(self):
        row1 = self.text1_area.document.cursor_position_row + 1
        row2 = self.text2_area.document.cursor_position_row + 1
        return f" ⬅{row1} ⬌ {row2}➡ "

    def run(self):
        if self.diff_ranges:
            self._goto_diff(0)
        self.app.run()


if __name__ == "__main__":
    text1 = """Hello world
This is a test
Another line
Line 4 here
Line 5 here
Line 6 here
Line 7 here
Line 8 here
Line 9 here
Line 10 here
"""

    text2 = """Hello Python
This is a test
Another line changed
Line 4 here changed
Line 5 here changed
Line 6 here changed
Line 7 here changed
Line 8 here changed1
Line 8 here
Line 9 here
Line 9 here
Line 10 here
"""
    ranges = DiffCalculator.calculate_diff_ranges(text1, text2)
    # Diff blocks
    diffs = [((1, 2), (1, 2)), ((4, 8), (4, 10))]

    viewer = TextDiffViewerApp(text1, text2, ranges)
    viewer.run()
