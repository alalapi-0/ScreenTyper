"""ScreenTyper 主程序入口。

该模块负责协调定时任务、读取输入内容并驱动屏幕输入操作。
"""

import argparse
import importlib.util
import platform
import sys
import time
from datetime import datetime
from typing import Optional

import schedule

from config import DEFAULT_INTERVAL_MINUTES, INPUT_FILE_PATH


def check_environment() -> None:
    """检查运行环境是否满足程序要求。"""

    print("=== ScreenTyper 环境检测 ===")

    # 检查操作系统是否为 Windows
    current_system = platform.system()
    if current_system != "Windows":
        print("⚠️ 当前系统非 Windows，本程序主要在 Windows 上测试，继续运行可能存在兼容性问题。")
    else:
        print(f"✅ 当前系统：{current_system}")

    # 检查 Python 版本是否符合最低要求
    python_version = sys.version.split(" ")[0]
    if sys.version_info < (3, 8):
        print(f"❌ 当前 Python 版本为 {python_version}，请升级至 3.8 或更高版本。")
        sys.exit(1)
    print(f"✅ Python 版本：{python_version}")

    # 检查必需依赖库是否已安装
    required_packages = ["schedule"]
    missing_packages = []

    for package in required_packages:
        # 通过 importlib.util.find_spec 判断模块是否存在
        if importlib.util.find_spec(package) is None:
            print(f"❌ 未检测到依赖：{package}")
            missing_packages.append(package)
        else:
            print(f"✅ 已安装 {package}")

    if missing_packages:
        print("❌ 环境检测失败，请安装缺失的依赖后重试。")
        sys.exit(1)

    print("🎉 环境检测通过，可以继续运行。")


def read_input_from_file(filepath: str) -> str:
    """读取指定文件中的文本内容。"""

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
    except FileNotFoundError:
        print(f"⚠️ 未找到输入文件：{filepath}")
        return ""
    except OSError as exc:
        print(f"⚠️ 读取输入文件时发生错误：{exc}")
        return ""

    # 去除首尾空白字符，防止出现额外的空行
    cleaned_content = content.strip()
    if not cleaned_content:
        print("⚠️ 输入文件内容为空，请检查文件。")
        return ""

    return cleaned_content


def trigger_typing_action() -> None:
    """触发一次模拟输入操作。"""

    content = read_input_from_file(INPUT_FILE_PATH)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("📄 当前输入内容：")
    if content:
        print(f"[模拟输入] {content}")
    else:
        print("[模拟输入] （输入内容为空，未执行实际输入）")

    print(f"🕒 已于 {timestamp} 触发模拟输入")


def schedule_typing_loop(interval_minutes: float) -> None:
    """根据给定的间隔循环调度输入任务。"""

    print("=== ScreenTyper 定时任务启动 ===")

    # 清理旧任务后注册新的定时任务
    schedule.clear()
    schedule.every(interval_minutes).minutes.do(trigger_typing_action)

    # 启动时立即执行一次，确保用户能够快速验证功能
    trigger_typing_action()

    try:
        announced_next_run: Optional[datetime] = None
        while True:
            schedule.run_pending()

            next_run = schedule.next_run()
            if next_run and next_run != announced_next_run:
                remaining_seconds = max((next_run - datetime.now()).total_seconds(), 0)
                remaining_minutes = remaining_seconds / 60
                print(
                    f"⏳ 等待下一次触发（约 {remaining_minutes:.1f} 分钟后，预计 {next_run.strftime('%Y-%m-%d %H:%M:%S')}）..."
                )
                announced_next_run = next_run

            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 检测到退出指令，正在结束定时任务。再见！")


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数，允许用户自定义任务间隔。"""

    parser = argparse.ArgumentParser(description="ScreenTyper 定时输入任务控制程序")
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL_MINUTES,
        help="定时触发间隔，单位为分钟，默认为配置文件中的数值。",
    )
    return parser.parse_args()


def validate_interval(interval_minutes: float) -> float:
    """验证并返回合法的间隔值。"""

    if interval_minutes <= 0:
        print("⚠️ 间隔必须为正数，将回退至默认值。")
        return DEFAULT_INTERVAL_MINUTES
    return interval_minutes


def main() -> None:
    """程序主入口，负责初始化并启动定时任务循环。"""

    args = parse_arguments()
    interval_minutes = validate_interval(args.interval)

    check_environment()
    schedule_typing_loop(interval_minutes)


if __name__ == "__main__":
    main()
