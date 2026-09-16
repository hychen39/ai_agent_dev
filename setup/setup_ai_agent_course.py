#!/usr/bin/env python3
"""以 Python 3.8+ 執行：python setup_ai_agent_course.py [專案目錄]。"""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request


MARKER = ".ai-agent-course-setup"


def run(args, cwd=None, env=None):
    print("\n> " + subprocess.list2cmdline([str(arg) for arg in args]), flush=True)
    subprocess.run([str(arg) for arg in args], cwd=cwd, env=env, check=True)


def ensure_uv():
    """使用現有 uv，否則執行官方 installer，安裝至使用者目錄。"""
    install_dir = Path.home() / ".local" / "bin"
    executable = "uv.exe" if os.name == "nt" else "uv"
    existing = shutil.which("uv")
    if existing:
        return Path(existing)
    uv = install_dir / executable
    if uv.is_file():
        return uv

    print("找不到 uv，將從 astral.sh 下載官方安裝程式。", flush=True)
    windows = os.name == "nt"
    shell = shutil.which("powershell.exe" if windows else "sh")
    if not shell:
        raise RuntimeError("找不到 PowerShell 或 sh，請請老師協助安裝 uv。")
    suffix = ".ps1" if windows else ".sh"
    url = "https://astral.sh/uv/install" + suffix
    env = os.environ.copy()
    env["UV_INSTALL_DIR"] = str(install_dir)
    with tempfile.TemporaryDirectory(prefix="uv-installer-") as temp:
        installer = Path(temp) / ("install" + suffix)
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                installer.write_bytes(response.read())
        except urllib.error.URLError:
            # 部分 Python 發行版缺少 CA 憑證，改用系統下載工具驗證 HTTPS。
            curl = shutil.which("curl.exe" if windows else "curl")
            if not curl:
                raise RuntimeError("下載失敗，請檢查網路及 Python 的 HTTPS 憑證設定。")
            run([curl, "--fail", "--location", "--show-error",
                 "--connect-timeout", "30", "--max-time", "180",
                 "--output", installer, url])
        if windows:
            run([shell, "-NoProfile", "-ExecutionPolicy", "Bypass",
                 "-File", installer], env=env)
        else:
            run([shell, installer], env=env)
    if not uv.is_file():
        raise RuntimeError("uv 安裝後未找到執行檔：" + str(uv))
    return uv


def write_new(path, content):
    """以獨佔建立保護既有檔案，尤其是金鑰與學生作業。"""
    try:
        with path.open("x", encoding="utf-8") as output:
            output.write(content)
    except FileExistsError:
        print("保留既有檔案：" + str(path))


def setup(project):
    marker = project / MARKER
    if project.exists() and not project.is_dir():
        raise RuntimeError("指定路徑已存在且不是資料夾：" + str(project))
    if project.exists() and any(project.iterdir()) and not marker.is_file():
        raise RuntimeError("目標資料夾已有其他檔案，請指定新的或空白的資料夾。")

    uv = ensure_uv()
    run([uv, "--version"])
    project.mkdir(parents=True, exist_ok=True)
    write_new(marker, "Created by setup_ai_agent_course.py\n")

    # 統一使用 Python 3.12；uv 會在需要時下載，不取代系統 Python。
    if not (project / "pyproject.toml").exists():
        run([uv, "init", "--name", "ai-agent-course", "--python", "3.12",
             "--no-workspace", "--vcs", "none", project])

    # 避免外部已啟用的環境或 uv 環境變數將套件裝到其他專案。
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    env.pop("UV_WORKING_DIRECTORY", None)
    env.pop("UV_PROJECT", None)
    env["UV_PROJECT_ENVIRONMENT"] = str(project / ".venv")
    run([uv, "add", "--dev", "ipykernel"], cwd=project, env=env)
    run([uv, "add", "python-dotenv", "langchain", "langchain-openai"],
        cwd=project, env=env)

    write_new(project / ".env", 'OPENAI_API_KEY=""\n')
    write_new(project / ".gitignore",
              ".env\n.venv/\n__pycache__/\n.ipynb_checkpoints/\n" + MARKER + "\n")
    notebooks = project / "notebooks"
    notebooks.mkdir(exist_ok=True)
    notebook = {
        "cells": [{"cell_type": "code", "execution_count": None,
                   "metadata": {}, "outputs": [], "source": []}],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    notebook["cells"][0]["id"] = "first-code-cell"
    write_new(notebooks / "first_openai_api.ipynb",
              json.dumps(notebook, ensure_ascii=False, indent=2) + "\n")

    python = project / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    run([python, "-c", "import ipykernel, dotenv, langchain, langchain_openai; "
         "print('課程套件載入成功')"], cwd=project)
    print("\n建置完成：" + str(project))
    print("1. 在 VS Code 開啟此資料夾（需已安裝 Python 與 Jupyter 擴充套件）。")
    print('2. 編輯 .env，在 OPENAI_API_KEY="" 的引號內填入自己的金鑰。')
    print("3. 開啟 notebooks/first_openai_api.ipynb。")
    print("4. 在右上角選取核心 → Python 環境，選擇此專案的 .venv。")
    print("   Python 路徑：" + str(python))
    print("若終端機找不到 uv，請關閉並重新開啟 VS Code／終端機。")
    print("uv 執行檔：" + str(uv))


def main():
    parser = argparse.ArgumentParser(description="建立 AI Agent 課程的 uv 專案。需要網路連線。")
    parser.add_argument("project", nargs="?", type=Path,
                        default=Path(__file__).resolve().parent / "ai_agent_course",
                        help="專案目錄，預設建立在本腳本旁的 ai_agent_course")
    args = parser.parse_args()
    try:
        setup(args.project.expanduser().resolve())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print("\n建置未完成：" + str(exc), file=sys.stderr)
        print("請確認資料夾可寫入，且網路允許下載 astral.sh、GitHub 與 PyPI 的檔案。\n"
              "若學校限制執行安裝程式，請請老師或管理員協助。修正後可重跑相同指令。",
              file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n已中止；可重新執行相同指令。", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
