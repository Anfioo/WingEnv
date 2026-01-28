from rich.console import Console
from rich.text import Text


def print_banner():
    console = Console(force_terminal=True)

    banner_str = r"""
     █████   ███   █████  ███   Powered by Anfioo  ██████████      Version     2.0.1
    ▒▒███   ▒███  ▒▒███  ▒▒▒                      ▒▒███▒▒▒▒▒█                       
     ▒███   ▒███   ▒███  ████  ████████    ███████ ▒███  █ ▒  ████████   █████ █████
     ▒███   ▒███   ▒███ ▒▒███ ▒▒███▒▒███  ███▒▒███ ▒██████   ▒▒███▒▒███ ▒▒███ ▒▒███ 
     ▒▒███  █████  ███   ▒███  ▒███ ▒███ ▒███ ▒███ ▒███▒▒█    ▒███ ▒███  ▒███  ▒███ 
      ▒▒▒█████▒█████▒    ▒███  ▒███ ▒███ ▒███ ▒███ ▒███ ▒   █ ▒███ ▒███  ▒▒███ ███  
        ▒▒███ ▒▒███      █████ ████ █████▒▒███████ ██████████ ████ █████  ▒▒█████   
         ▒▒▒   ▒▒▒      ▒▒▒▒▒ ▒▒▒▒ ▒▒▒▒▒  ▒▒▒▒▒███▒▒▒▒▒▒▒▒▒▒ ▒▒▒▒ ▒▒▒▒▒    ▒▒▒▒▒    
        ___          _____                ███ ▒███                                  
       /   |  ____  / __(_)___  ____     ▒▒██████                                   
      / /| | / __ \/ /_/ / __ \/ __ \     ▒▒▒▒▒▒                                                                 
     / ___ |/ / / / __/ / /_/ / /_/ /                            
    /_/  |_/_/ /_/_/ /_/\____/\____/              https://github.com/Anfioo/WingEnv
    """

    banner = banner_str.strip("\n").split("\n")

    def lerp(a, b, t):
        return int(a + (b - a) * t)

    def hex_to_rgb(hex_color):
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
        # 输出: (255, 255, 0)
        return rgb

    block_start = (0, 255, 255)  # cyan
    block_end = (255, 0, 255)  # magenta

    shade_start = (80, 120, 255)  # soft blue
    shade_end = (160, 80, 200)  # purple

    anfioo_start = (255, 0, 255)
    anfioo_end = (255, 255, 0)

    # backgrobbackground: linear-gradient(135deg, # 0%, # 100%);

    width = max(len(line) for line in banner)

    for line in banner:
        text = Text()
        for i, ch in enumerate(line):
            if ch == " ":
                text.append(ch)
                continue

            t = i / max(width - 1, 1)

            if ch == "█":
                r = lerp(block_start[0], block_end[0], t)
                g = lerp(block_start[1], block_end[1], t)
                b = lerp(block_start[2], block_end[2], t)
                style = f"bold rgb({r},{g},{b})"

            elif ch == "▒":
                r = lerp(shade_start[0], shade_end[0], t)
                g = lerp(shade_start[1], shade_end[1], t)
                b = lerp(shade_start[2], shade_end[2], t)
                style = f"rgb({r},{g},{b})"

            else:
                r = lerp(anfioo_start[0], anfioo_end[0], t)
                g = lerp(anfioo_start[1], anfioo_end[1], t)
                b = lerp(anfioo_start[2], anfioo_end[2], t)
                style = f"rgb({r},{g},{b})"

            text.append(ch, style=style)

        console.print(text)


