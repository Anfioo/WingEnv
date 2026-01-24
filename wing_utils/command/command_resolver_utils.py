import json
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


# =========================
# 类型定义
# =========================

class CommandType(Enum):
    RAW = "raw"          # python --version
    REWRITE = "rewrite"  # we-re
    RUN = "run"          # we-run


@dataclass
class CommandMatch:
    type: CommandType
    desc: str
    commands: List[str]


# =========================
# Resolver
# =========================

class WeCommandResolver:

    def __init__(self, config_path: str):
        self.config = self._load(config_path)

    @staticmethod
    def _load(path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def resolve(
        self,
        tool: str,
        args: List[str]
    ) -> Optional[CommandMatch]:
        """
        tool: conda / python
        args: ["conf", "ls"]
        """
        tool_map = self.config.get("tools", {}).get(tool)
        if not tool_map:
            return None

        for path in self._build_paths(args):
            node = tool_map.get(path)
            if not node:
                continue

            desc, actions = next(iter(node.items()))
            return self._parse_actions(tool, desc, actions)

        return None

    @staticmethod
    def _build_paths(args: List[str]) -> List[str]:
        """
        ["conf", "ls"] -> ["conf ls", "conf"]
        """
        return [" ".join(args[:i]) for i in range(len(args), 0, -1)]

    @staticmethod
    def _parse_actions(
        tool: str,
        desc: str,
        actions
    ) -> CommandMatch:
        """
        actions: str | List[str]
        """
        if isinstance(actions, str):
            actions = [actions]

        commands: List[str] = []
        cmd_type = CommandType.RAW

        for act in actions:
            if act.startswith("we-re:"):
                cmd_type = CommandType.REWRITE
                commands.append(act[len("we-re:"):].strip())

            elif act.startswith("we-run:"):
                cmd_type = CommandType.RUN
                commands.append(act[len("we-run:"):].strip())

            else:
                cmd_type = CommandType.RAW
                commands.append(f"{tool} {act}".strip())

        return CommandMatch(
            type=cmd_type,
            desc=desc,
            commands=commands
        )


# =========================
# 示例
# =========================

if __name__ == "__main__":
    resolver = WeCommandResolver("we_commands.json")

    match = resolver.resolve("conda", ["conf", "ls"])
    print(match)

    match = resolver.resolve("python", ["v"])
    print(match)

    match = resolver.resolve("conda", ["info"])
    print(match)
