from typing import List, Tuple, Optional
import difflib


# ===================== 新增的差异计算工具类 =====================
class DiffCalculator:
    """
    文本差异计算工具类，用于自动对比两个文本的行差异，生成符合视图要求的差异范围列表
    """

    @staticmethod
    def _get_line_blocks(matches: List[Tuple[int, int, int]], text1_lines: List[str], text2_lines: List[str]) -> List[
        Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        从difflib的匹配结果中提取差异块，转换为1-based的行号范围
        """
        diff_blocks = []
        prev_end1, prev_end2 = 0, 0
        len1, len2 = len(text1_lines), len(text2_lines)

        # 处理所有匹配块之间的差异区域
        for match_start1, match_start2, match_len in matches:
            # 计算当前匹配块之前的差异区域
            diff_start1 = prev_end1
            diff_end1 = match_start1
            diff_start2 = prev_end2
            diff_end2 = match_start2

            # 如果存在差异区域（非空）
            if diff_start1 < diff_end1 or diff_start2 < diff_end2:
                # 转换为1-based行号（闭区间）
                block1 = (diff_start1 + 1, diff_end1) if diff_start1 < diff_end1 else (0, 0)
                block2 = (diff_start2 + 1, diff_end2) if diff_start2 < diff_end2 else (0, 0)

                # 过滤掉无效的空块
                if block1 != (0, 0) or block2 != (0, 0):
                    diff_blocks.append((block1, block2))

            # 更新上一个匹配块的结束位置
            prev_end1 = match_start1 + match_len
            prev_end2 = match_start2 + match_len

        # 处理最后一个匹配块之后的剩余差异区域
        diff_start1 = prev_end1
        diff_end1 = len1
        diff_start2 = prev_end2
        diff_end2 = len2

        if diff_start1 < diff_end1 or diff_start2 < diff_end2:
            block1 = (diff_start1 + 1, diff_end1) if diff_start1 < diff_end1 else (0, 0)
            block2 = (diff_start2 + 1, diff_end2) if diff_start2 < diff_end2 else (0, 0)
            if block1 != (0, 0) or block2 != (0, 0):
                diff_blocks.append((block1, block2))

        return diff_blocks

    @staticmethod
    def calculate_diff_ranges(text1: str, text2: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        核心方法：计算两个文本的差异行范围，返回格式为 [( (start1, end1), (start2, end2) )]
        - start/end 都是1-based的行号（闭区间）
        - 例如 ((1,2), (1,2)) 表示text1的1-2行和text2的1-2行是差异区域
        """
        # 按行分割文本（保留空行）
        text1_lines = text1.splitlines(keepends=False)
        text2_lines = text2.splitlines(keepends=False)

        # 如果任一文本为空，直接返回全量差异
        if not text1_lines and not text2_lines:
            return []
        if not text1_lines:
            return [((0, 0), (1, len(text2_lines)))]
        if not text2_lines:
            return [((1, len(text1_lines)), (0, 0))]

        # 使用difflib计算匹配块
        matcher = difflib.SequenceMatcher(None, text1_lines, text2_lines)
        # 获取所有匹配块（start1, start2, length），按位置排序
        matches = sorted(matcher.get_matching_blocks(), key=lambda x: (x[0], x[1]))

        # 提取并转换差异块
        diff_blocks = DiffCalculator._get_line_blocks(matches, text1_lines, text2_lines)

        return diff_blocks
