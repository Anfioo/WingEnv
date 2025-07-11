import difflib


class StrManipulator:
    @staticmethod
    def insert_after(original: str, target: str, to_insert: str) -> str:
        index = original.find(target)
        if index == -1:
            return original
        return original[:index + len(target)] + to_insert + original[index + len(target):]

    @staticmethod
    def insert_before(original: str, target: str, to_insert: str) -> str:
        index = original.find(target)
        if index == -1:
            return original
        return original[:index] + to_insert + original[index:]

    @staticmethod
    def insert_between(original: str, start: str, end: str, to_insert: str) -> str:
        """
        在两个字符串之间插入内容，仅第一次匹配
        """
        start_index = original.find(start)
        if start_index == -1:
            return original
        end_index = original.find(end, start_index + len(start))
        if end_index == -1:
            return original
        insert_pos = start_index + len(start)
        return original[:insert_pos] + to_insert + original[insert_pos:]

    @staticmethod
    def replace_once(original: str, old: str, new: str) -> str:
        return original.replace(old, new, 1)

    @staticmethod
    def replace_between(original: str, start: str, end: str, replacement: str) -> str:
        """
        将 start 和 end 之间的内容替换为 replacement
        """
        start_index = original.find(start)
        if start_index == -1:
            return original
        end_index = original.find(end, start_index + len(start))
        if end_index == -1:
            return original
        return original[:start_index + len(start)] + replacement + original[end_index:]

    @staticmethod
    def insert_after_substring(original: str, target: str, to_insert: str) -> str:
        """
        在原始字符串中，找到目标子串 target，并在其后插入字符串 to_insert。
        如果 target 未找到，返回原始字符串。
        """
        index = original.find(target)
        if index == -1:
            return original  # 找不到就原样返回
        insert_pos = index + len(target)
        return original[:insert_pos] + to_insert + original[insert_pos:]




def get_diff_blocks_with_line_numbers(original: str, modified: str) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    orig_lines = original.splitlines()
    mod_lines = modified.splitlines()
    diff = difflib.ndiff(orig_lines, mod_lines)

    diffs = []

    orig_start = None
    orig_end = None
    mod_start = None
    mod_end = None

    orig_line_no = 0
    mod_line_no = 0

    def push_diff():
        nonlocal orig_start, orig_end, mod_start, mod_end
        if orig_start is None and mod_start is None:
            return  # 无差异
        # 用0表示无对应行，避免 None
        o_start = orig_start if orig_start is not None else 0
        o_end = orig_end if orig_end is not None else o_start
        m_start = mod_start if mod_start is not None else 0
        m_end = mod_end if mod_end is not None else m_start

        # 如果原始是(0, 0)，且修改后有有效行，则原始区间改为修改后起始+1
        if o_start == 0 and m_start > 0:
            o_start = m_start + 1
            o_end = o_start + 1

        diffs.append(((o_start, o_end), (m_start, m_end)))
        orig_start = orig_end = None
        mod_start = mod_end = None

    for d in diff:
        code = d[:2]
        line = d[2:]

        if code == '  ':  # 相同行
            if orig_start is not None or mod_start is not None:
                push_diff()
            orig_line_no += 1
            mod_line_no += 1

        elif code == '- ':
            if orig_start is None:
                orig_start = orig_line_no + 1
            orig_end = orig_line_no + 1
            orig_line_no += 1

        elif code == '+ ':
            if mod_start is None:
                mod_start = mod_line_no + 1
            mod_end = mod_line_no + 1
            mod_line_no += 1

    # 最后一块差异
    if orig_start is not None or mod_start is not None:
        push_diff()

    return diffs


