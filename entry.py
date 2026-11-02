# -*- coding: utf-8 -*-
"""农银14净值看板 —— 双击即用的打包入口。

行为：
    1. 抓取农银理财官网最新净值
    2. 在 exe 所在目录生成「农银14看板.html」
    3. 自动用默认浏览器打开

打包：
    pyinstaller --onefile --console --name abc1409 entry.py
"""
import sys
import traceback
import webbrowser
from pathlib import Path


def base_dir() -> Path:
    """exe 所在目录（打包后）；源码运行时为脚本目录。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def fix_console_encoding() -> None:
    """把 Windows 控制台切到 UTF-8，避免中文乱码。"""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:  # noqa: BLE001
        pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass


def pause() -> None:
    try:
        input("\n按回车键退出...")
    except (EOFError, KeyboardInterrupt):
        pass


def main() -> int:
    fix_console_encoding()
    print("=" * 46)
    print("  农银匠心灵动14天 第9期G · 净值看板")
    print("=" * 46)
    print()
    print("正在抓取最新净值，请稍候 ...")

    try:
        from fetch_core import build, fetch_navs, render
    except Exception as exc:  # noqa: BLE001
        print(f"\n[错误] 程序内部模块加载失败：{exc}")
        traceback.print_exc()
        pause()
        return 1

    try:
        navs = fetch_navs()
        if not navs:
            raise RuntimeError("未取到任何净值记录")
        d = build(navs)
        html = render(d)
    except Exception as exc:  # noqa: BLE001
        print(f"\n[失败] 抓取或生成出错：{exc}")
        print("\n可能原因：网络不通、农银官网暂时不可访问、或代理拦截。")
        traceback.print_exc()
        pause()
        return 1

    out = base_dir() / "农银14看板.html"
    try:
        out.write_text(html, encoding="utf-8")
    except OSError as exc:
        print(f"\n[失败] 无法写入文件：{out}\n{exc}")
        pause()
        return 1

    print()
    print(f"最新净值日  {d['latest_date']}")
    print(f"单位净值    {d['latest_nav']:.6f}")
    wan = d["latest_wan"]
    print(f"万份收益    {'—' if wan is None else f'{wan:+.2f} 元'}")
    print(f"状态        {'已更新' if d['fresh'] else '待更新（今日尚未披露）'}")
    print()
    print(f"已生成：{out}")
    print("正在打开浏览器 ...")

    try:
        webbrowser.open(out.as_uri())
    except Exception:  # noqa: BLE001
        print("（自动打开失败，请手动双击该 html 文件）")

    print()
    print("完成。以后想更新数据，再双击本程序即可。")
    pause()
    return 0


if __name__ == "__main__":
    sys.exit(main())
