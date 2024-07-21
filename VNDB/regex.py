import re
from typing import overload  # , override
from api import vndb_query

vndb_query.__override__ = True


@overload
def vn_query(name: str, translated: bool = True, **args: dict[str, str]) -> str:
    pass


# 正则测试
if __name__ == "__main__":
    raw = "/vndb_game GINKA 会社 FrontWing 角色 cv 长谷川育美 汉化"
    keys = ["会社", "角色", "cv"]
    match = re.findall(rf'({"|".join(keys)})\s+(?!(?:{"|".join(keys)}))(\S+)?', raw)
    print(match)  # [('会社', 'FrontWing'), ('cv', '长谷川育美')]
    """
    results = vndb_query(
        "character",
        {  # 新建查询的时候可以把这个复制过去
            "filters": [
                "and",
                # ["search", "=", "Sion"],# 直接搜索
                ["birthday", "=", [f"{1}", f"{2}"]],  # 生日日期
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
    """
