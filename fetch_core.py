# -*- coding: utf-8 -*-
"""轻量封装：把 fetch_and_build 的抓取/计算与模板渲染拆出来，供 exe 调用。"""
import json

from fetch_and_build import build, fetch_navs, TPL  # noqa: F401


def render(d: dict) -> str:
    """把数据渲染成完整 HTML 字符串。"""
    return (TPL
            .replace("__NAME__", d["name"])
            .replace("__CODE__", d["code"])
            .replace("__N__", str(len(d["daily"])))
            .replace("__BUILT__", d["built_at"])
            .replace("__DATA__", json.dumps(d, ensure_ascii=False)))
