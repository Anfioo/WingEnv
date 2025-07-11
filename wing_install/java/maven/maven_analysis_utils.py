import requests
from bs4 import BeautifulSoup
import re

def get_maven_windows_links(url="https://maven.apache.org/download.cgi"):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a', href=True)
        zip_links = []

        for link in links:
            href = link['href']
            text = link.get_text(strip=True)

            # 找出包含 bin.zip 的链接（即 Windows zip 安装包）
            if re.search(r'apache-maven-[\d.]+-bin\.zip$', href):
                zip_links.append({
                    'version': re.search(r'apache-maven-([\d.]+)-bin\.zip', href).group(1),
                    'download_link': href,
                    'filename': text
                })

        return zip_links

    except Exception as e:
        print(f"获取 Maven 下载链接出错: {e}")
        return []

# 示例运行
if __name__ == "__main__":
    links = get_maven_windows_links()
    for item in links:
        print(f"Maven {item['version']}: {item['download_link']}")
