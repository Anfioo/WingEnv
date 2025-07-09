import requests
from bs4 import BeautifulSoup
import re


def get_openjdk_archives(url):
    """从OpenJDK归档页面获取版本信息，只保留Windows平台"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        all_versions = []

        rows = soup.select('table.builds tr')
        if not rows:
            return all_versions

        current_version = None

        for row in rows:
            cells = row.find_all(['th', 'td'])
            if not cells:
                continue

            cell_texts = [cell.get_text(strip=True) for cell in cells]

            # 检测版本标题行
            if len(cells) == 1 and cells[0].name == 'th':
                if current_version:
                    all_versions.append(current_version)
                current_version = parse_version_header(cells[0].get_text(strip=True))
                continue

            # 检测Source行（版本结束标志）
            if len(cells) >= 3 and 'Source' in cell_texts[0]:
                if current_version:
                    current_version['source'] = {
                        'link': cells[1].find('a')['href'] if cells[1].find('a') else '',
                        'tag': cell_texts[2] if len(cell_texts) > 2 else ''
                    }
                    all_versions.append(current_version)
                    current_version = None
                continue

            # 处理平台行（只保留Windows平台）
            if current_version and len(cells) >= 3 and cells[0].get_text(strip=True):
                platform = parse_platform_row(cells)
                if platform and 'Windows' in platform['os']:
                    current_version['platforms'].append(platform)

        # 添加最后一个版本
        if current_version:
            all_versions.append(current_version)

        # 过滤掉没有Windows平台的版本
        all_versions = [v for v in all_versions if v['platforms']]

        return all_versions

    except Exception as e:
        print(f"获取版本信息出错: {e}")
        return []


def parse_version_header(header_text):
    """解析版本标题行，提取版本号和构建号"""
    # 处理类似 "9 GA (build 9+181)" 的格式
    ga_match = re.match(r'(\d+)\s+GA\s*\(build\s*([\d.+\-]+)\)', header_text)
    if ga_match:
        return {
            'version': f"{ga_match.group(1)}.GA",
            'build': ga_match.group(2),
            'platforms': []
        }

    # 处理类似 "10 GA (build 10+46)" 的格式
    ga_dot_match = re.match(r'(\d+\.\d+)\s+GA\s*\(build\s*([\d.+\-]+)\)', header_text)
    if ga_dot_match:
        return {
            'version': f"{ga_dot_match.group(1)}.GA",
            'build': ga_dot_match.group(2),
            'platforms': []
        }

    # 处理常规格式
    version_match = re.match(r'([\d.]+)\s*\(build\s*([\d.+\-]+)\)', header_text)
    if version_match:
        return {
            'version': version_match.group(1),
            'build': version_match.group(2),
            'platforms': []
        }

    # 处理无法匹配的情况
    return {
        'version': header_text,
        'build': '',
        'platforms': []
    }


def parse_platform_row(cells):
    """解析平台行，提取操作系统、架构和下载信息"""
    try:
        os_type = cells[0].get_text(strip=True)
        architecture = cells[1].get_text(strip=True)

        # 跳过Source相关行
        if 'Source' in os_type or 'Source' in architecture:
            return None

        # 提取下载链接和SHA256链接
        links = cells[2].find_all('a')
        download_link = links[0]['href'] if links else ''
        sha256_link = links[1]['href'] if len(links) > 1 else ''

        # 提取文件大小（直接解析文本）
        cell_content = cells[2]
        file_size_text = cell_content.get_text(strip=True)

        # 移除所有链接文本和HTML标签
        for a in cell_content.find_all('a'):
            a.extract()

        # 清理后的文本即为文件大小
        file_size_text = cell_content.get_text(strip=True).replace("(", "").replace(")", "")
        file_size = file_size_text.replace(',', '')  # 移除逗号分隔符

        # 处理文件大小单位
        file_size_formatted = process_file_size(file_size_text)

        return {
            'os': os_type,
            'architecture': architecture,
            'package': download_link.split('.')[-1] if download_link else '',
            'download_link': download_link,
            'sha256_link': sha256_link,
            'file_size': file_size,
            'file_size_human': file_size_text,
            'file_size_formatted': file_size_formatted
        }
    except Exception as e:
        print(f"解析平台行出错: {e}")
        return None


def process_file_size(size_text):
    """处理文件大小，带M单位的直接保留，否则转换为MB"""
    # 去除可能的空格
    size_text = size_text.strip()

    # 检查是否包含M单位
    if 'M' in size_text or 'MB' in size_text:
        return size_text
    else:
        try:
            # 尝试转换为字节数
            bytes_size = int(size_text)
            # 转换为MB并四舍五入
            mb_size = bytes_size / (1024 * 1024)
            return f"{int(round(mb_size))}M"
        except (ValueError, ZeroDivisionError):
            return size_text
