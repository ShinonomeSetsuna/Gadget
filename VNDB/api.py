from collections import defaultdict
from typing import Optional
import requests
import json


def has_language(targets: str | tuple[str], vns: list) -> bool:
    """判断某部vn是否具有目标语言(可匹配多种)

    Args:
        targets (str | tuple[str]): 目标语言，`str`或`tuple[str]`
        vns (list): api返回的`vns:dict`

    Returns:
        bool: 是否存在目标语言
    """
    for vn in vns:
        if isinstance(targets, str):
            if targets in vn["languages"]:
                return True
        if isinstance(targets, tuple):
            for target in targets:
                if target in vn["languages"]:
                    return True
    return False


def get_title(vn: dict, order: tuple[str]) -> str:
    """获取标题, 可以按优先级设置多种语言, e.g. `('zh-Hans', 'zh-Hant','ja')`

    Args:
        vn (dict): api返回的`vn`
        order (tuple[str]): 对标题语言的期望顺序

    Returns:
        str: 标题字符串
    """
    titles = vn["titles"]
    hm = defaultdict(str)

    for title in titles:
        if title["lang"] in order:
            hm[title["lang"]] = title["title"]

    for key in order:
        if key in hm:
            return hm[key]

    return ""


def vndb_query(endpoint: str, data: dict) -> Optional[dict]:
    """对vndb进行查询

    Args:
        endpoint (str): 查询的分类, 如`vn`, `character`等
        data (dict): 查询的内容
    """
    r = requests.post(
        f"https://api.vndb.org/kana/{endpoint}",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data),
    )

    try:
        results = r.json()
        return results
    except Exception:
        print(f"Error: {r.text}")
        return None


def birthday_query(month: int, day: int) -> str:
    """根据生日查询女主角

    Args:
        month (int): 出生月份
        day (int): 出生日期

    Returns:
        str: 查询结果
    """

    results = vndb_query(
        "character",
        {  # 新建查询的时候可以把这个复制过去
            "filters": [
                "and",
                # ["search", "=", "Sion"],# 直接搜索
                ["birthday", "=", [f"{month}", f"{day}"]],  # 生日日期
                ["sex", "=", "f"],  # 性别
                [
                    "or",
                    ["role", "=", "primary"],  # 主要角色
                    ["role", "=", "main"],  # 主要角色
                ],
            ],
            "fields": ", ".join(
                [
                    "id",
                    "name",
                    "original",
                    "aliases",
                    "vns.languages",
                    "vns.titles.title",
                    "vns.titles.lang",
                    "vns.release.id",
                ]
            ),  # 返回值
            "results": 100,  # 每页结果数
            "page": 1,  # 页数
            "count": True,  # 统计符合条件的总数
            "sort": "id",  # 排序方式
            # "reverse": True,  # 逆序
        },
    )

    if results is None:
        return "查询错误。"

    if len(results["results"]) == 0:
        return "查询结果为空。"

    # 过滤不包含目标语言的角色
    results["results"] = [
        result
        for result in results["results"]
        if has_language(("zh-Hans", "zh-Hant"), result["vns"])
    ]

    # 重新计数count
    # 理论上单日应该不会超过100, 出bug再改
    results["count"] = len(results["results"])

    return "\n".join(
        [
            "\t".join(
                [
                    result["original"] or result["name"],
                    get_title(result["vns"][0], ("zh-Hans", "zh-Hant", "ja", "en")),
                    result["vns"][0]["id"],
                ]
            )
            for result in results["results"]
        ]
    )


if __name__ == "__main__":
    print(birthday_query(5, 18))
