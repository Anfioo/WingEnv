def read_file_to_string(file_path: str, encoding: str = 'utf-8') -> str:
    """
    读取指定路径的文件内容，并以字符串形式返回。

    :param file_path: 文件的完整路径
    :param encoding: 文件编码，默认 utf-8
    :return: 文件内容的字符串
    """
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"文件未找到：{file_path}")
    except Exception as e:
        raise RuntimeError(f"读取文件失败：{e}")



def write_string_to_file(file_path: str, content: str, encoding: str = 'utf-8') -> None:
    """
    将字符串内容写入到指定文件路径中，会覆盖原有内容。

    :param file_path: 文件的完整路径
    :param content: 要写入的字符串内容
    :param encoding: 写入时使用的编码，默认 utf-8
    """
    try:
        with open(file_path, 'w', encoding=encoding) as file:
            file.write(content)
    except Exception as e:
        raise RuntimeError(f"写入文件失败：{e}")

