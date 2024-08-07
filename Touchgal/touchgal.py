from dataclasses import dataclass
from urllib.parse import quote
import requests

from dataclasses import is_dataclass, fields
from typing import Literal, get_args

# 如果有问题的话就把这个cookie改了
# 试了一下好像不需要cookie，不过要是哪天用不了了再看看是不是这的问题吧
COOKIE = ""
# COOKIE = "PUT_YOUR_COOKIE_HERE"


def from_dict(data_class: type, data: dict):
    """根据dict生成对应的dataclass实例

    Args:
        data_class (type): dataclass类
        data (dict): 数据

    Returns:
        DataClassInstance: 对应dataclass实例
    """
    if not is_dataclass(data_class):
        raise ValueError(f"{data_class} is not a dataclass")

    fieldtypes = {f.name: f.type for f in fields(data_class)}
    return data_class(
        **{
            f: from_dict(fieldtypes[f], data[f])
            if is_dataclass(fieldtypes[f])
            else (
                [from_dict(args, item) for item in data[f]]
                if is_dataclass(args := (get_args(fieldtypes[f]) or [None])[0])
                else data[f]
            )
            for f in data
        }
    )


@dataclass
class QueryResponseDataItemSource:
    name: str
    size: int


@dataclass
class QueryResponseDataItem:
    key: str
    is_dir: bool
    password: str
    create_date: str
    downloads: int
    remain_downloads: int
    views: int
    expire: int
    preview: bool
    source: QueryResponseDataItemSource


@dataclass
class QueryResponseData:
    items: list[QueryResponseDataItem]
    total: int


@dataclass
class QueryResponse:
    code: int
    data: QueryResponseData
    msg: str


@dataclass
class DownloadResponse:
    code: int
    data: str
    msg: str


@dataclass
class DownloadDirResponseDataObject:
    id: str
    name: str
    path: str
    thumb: bool
    size: int
    type: Literal["file"]
    date: str
    create_date: str
    key: str
    source_enabled: bool


@dataclass
class DownloadDirResponseData:
    objects: list[DownloadDirResponseDataObject]


@dataclass
class DownloadDirResponse:
    code: int
    data: DownloadDirResponseData
    msg: str


def gal_query(keyword: str) -> QueryResponse:
    keyword = quote(keyword)  # 有些中文不支持……
    """在TouchGal进行资源搜索

    Args:
        keyword (str): 关键字

    Returns:
        QueryResponse: 查询结果
    """
    URL = f"https://pan.touchgal.net/api/v3/share/search?page=1&order_by=created_at&order=DESC&keywords={keyword}"
    header = {
        "Accept": "application/json, text/plain, */*",
        "Cookie": COOKIE,
        "Referer": f"https://pan.touchgal.net/search?keywords={keyword}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    }
    data = {}
    r = requests.get(URL, headers=header, json=data)

    try:
        return from_dict(QueryResponse, r.json())
    except Exception:
        # 目前还不知道查询错误有哪些
        return r.json()["msg"]


def dir_download(key: str) -> list[str]:
    key = quote(key)
    """对文件夹进行下载

    Args:
        key (str): 文件的key

    Returns:
        list[str]: 下载链接[列表]
    """
    header = {
        "Accept": "application/json, text/plain, */*",
        "Cookie": COOKIE,
        "Referer": f"https://pan.touchgal.net/s/{key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    }
    URL = f"https://pan.touchgal.net/api/v3/share/list/{key}%2F"
    data = {}
    rd: DownloadDirResponse = from_dict(
        DownloadDirResponse, requests.get(URL, headers=header, json=data).json()
    )
    if rd.code == 0:
        return [
            file_download(f"{item.key}?path={item.path}{item.name}")
            for item in rd.data.objects
        ]
    else:
        return [rd.msg]


def file_download(key: str) -> str:
    key = quote(key, safe="?=/")
    """对文件进行下载

    Args:
        key (str): 文件的key

    Returns:
        str: 下载链接
    """
    header = {
        "Accept": "application/json, text/plain, */*",
        "Cookie": COOKIE,
        "Referer": f"https://pan.touchgal.net/s/{key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    }

    URL = f"https://pan.touchgal.net/api/v3/share/download/{key}"
    data = {}

    r: DownloadResponse = from_dict(
        DownloadResponse, requests.put(URL, headers=header, json=data).json()
    )
    if r.code == 0:
        return r.data
    else:
        return r.msg


def gal_download(r: QueryResponseDataItem) -> list[str]:
    """在TouchGal中获取下载链接

    Args:
        r (QueryResponseDataItem): 查询中返回结果

    Returns:
        list[str]: 下载链接[列表]
    """
    if r.is_dir:
        return dir_download(r.key)
    else:
        return [file_download(r.key)]


# Example
if __name__ == "__main__":
    keyword = input("请输入搜索内容:")

    r = gal_query(
        keyword
    )  # 返回结果可以看一下上面的class, 如果不知道可以根据自动补全去猜（x

    if r.code == 0:
        print(f"关键字{keyword}的查询结果(共{r.data.total}个):")
        for i, item in enumerate(r.data.items):
            print(f"{i + 1}、{item.source.name}")
    else:
        print(f"出现错误：{r.msg}")

    if r.data.total != 0:
        # 这里是 QueryResponse.data.items:QueryResponseDataItem
        # 修改后面的序号就可以
        for link in gal_download(r.data.items[int(input("选择链接:")) - 1]):
            print(link)
