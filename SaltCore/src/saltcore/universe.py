"""第一阶段研究名单：人工选择的排名快照，运行时不重算排名。"""

import json
from importlib.resources import files


def core_universe() -> list[dict]:
    """返回排名前十；是已验证的研究范围，不限制读取层扩展其他品种。"""
    return json.loads(
        files("saltcore").joinpath("data/core_universe.json").read_text()
    )["products"]
