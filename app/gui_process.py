# app/gui_process.py（真正最终修复版）
"""
完整的配置 GUI 实现（独立进程运行）
关键修复：子进程只在必要时启动，而且不会重复初始化
"""
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import subprocess
from pathlib import Path
import webbrowser
import gc

from app.state_file import get_next_refresh_time

# 取得项目根目录
this_file_dir = Path(__file__).resolve().parent
project_root = this_file_dir.parent

# 如果项目根目录还没在 sys.path 里，加进去
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 同时强制把 cwd 也设成根目录
os.chdir(project_root)

from app.config import CONFIG, CONFIG_SCHEMA

LOCK_FILE = Path.home() / ".update-weather" / "gui.lock"
LOCK_FILE.parent.mkdir(exist_ok=True)

# ================== 单实例管理 ==================
def is_gui_running():
    """检查是否有存活的 GUI 进程"""
    if not LOCK_FILE.exists():
        return None

    try:
        pid_str = LOCK_FILE.read_text().strip()
        if not pid_str.isdigit():
            raise ValueError("锁文件内容不是有效 PID")
        pid = int(pid_str)
    except Exception as e:
        print(f"锁文件无效或损坏，自动清理: {e}")
        LOCK_FILE.unlink(missing_ok=True)
        return None

    try:
        os.kill(pid, 0)  # 检查进程是否存在
        return pid
    except OSError:
        print(f"旧 GUI 进程 (pid={pid}) 已不存在，清理锁文件")
        LOCK_FILE.unlink(missing_ok=True)
        return None


def activate_existing_gui(pid: int):
    """尝试激活旧窗口，失败时打印日志但不影响新窗口"""
    print(f"检测到已有实例 (pid={pid})，尝试激活...")
    try:
        result = subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "System Events" to set frontmost of the first process whose unix id is {pid} to true'
            ],
            check=False,
            timeout=4,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("激活成功")
        else:
            err_msg = result.stderr.strip() or "未知错误"
            print(f"激活失败: {err_msg}")
    except Exception as e:
        print(f"激活过程中异常: {e}")


def write_lock():
    LOCK_FILE.write_text(str(os.getpid()))
    print(f"写入锁文件: pid={os.getpid()}")


def remove_lock():
    """安全清理锁文件"""
    try:
        LOCK_FILE.unlink(missing_ok=True)
        print("锁文件已清理")
    except Exception as e:
        print(f"清理锁文件失败: {e}")


def center_window(root, width, height):
    """窗口居中"""
    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")


# ================== 配置界面构建 ==================
class ConfigGUI:
    def __init__(self, root):
        self.root = root
        self.widgets = {}

        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill="both", expand=True)

        self.status_label = ttk.Label(
            main_frame,
            text="加载中...",
            font=("Helvetica", 14, "bold"),
            foreground="#333333"
        )
        self.status_label.pack(pady=(0, 15))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # 一次性创建所有 Tab 内容
        self.create_refresh_tab()
        self.create_night_tab()
        self.create_weather_tab()
        self.create_mail_tab()

        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(15, 15))

        save_btn = ttk.Button(
            btn_frame,
            text="保存配置",
            command=self.save_config,
            width=15
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(
            btn_frame,
            text="取消",
            command=self.cancel,
            width=15
        )
        cancel_btn.pack(side="left", padx=5)

        # 窗口打开后立即更新状态
        self.update_status_label()

        # 每 10 秒刷新一次状态
        self.root.after(10000, self.periodic_update_status)

        self.root.update_idletasks()
        gc.collect()

    def update_status_label(self):
        try:
            from app.state_file import get_next_refresh_time

            next_time = get_next_refresh_time()

            if next_time is None:
                next_str = "未设置（调度器启动中...）"
                status = "服务初始化中"
                color = "orange"
            else:
                now = datetime.datetime.now()
                next_str = next_time.strftime("%Y-%m-%d %H:%M")
                if next_time > now:
                    status = "服务运行中"
                    color = "green"
                else:
                    status = "已过期（即将刷新）"
                    color = "orange"

            text = f"下次刷新：{next_str}   |   {status}"
            self.status_label.config(text=text, foreground=color)
        except Exception as e:
            self.status_label.config(text=f"读取状态失败：{str(e)}", foreground="red")

    def periodic_update_status(self):
        """定时更新状态"""
        self.update_status_label()
        self.root.after(10000, self.periodic_update_status)

    def create_refresh_tab(self):
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="刷新设置")

        ttk.Label(frame, text="刷新间隔（分钟）:", font=("Helvetica", 11)).grid(row=0, column=0, sticky="w", pady=10)
        interval_var = tk.IntVar(value=CONFIG.refresh_interval_minutes)
        interval_spin = ttk.Spinbox(frame, from_=1, to=1440, textvariable=interval_var, width=15)
        interval_spin.grid(row=0, column=1, padx=20, pady=10)
        ttk.Label(frame, text="建议: 30-120 分钟", foreground="gray").grid(row=1, column=1, sticky="w", padx=20)

        midnight_var = tk.BooleanVar(value=CONFIG.force_refresh_at_midnight)
        midnight_check = ttk.Checkbutton(
            frame,
            text="每天 0 点强制刷新一次",
            variable=midnight_var
        )
        midnight_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=10)

        ttk.Label(
            frame,
            text="无论间隔多久，每天凌晨都会强制更新一次",
            foreground="gray",
            font=("Helvetica", 11)
        ).grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 10))

        self.widgets["refresh.interval_minutes"] = interval_var
        self.widgets["refresh.force_refresh_at_midnight"] = midnight_var

    def create_night_tab(self):
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="夜间模式")

        skip_var = tk.BooleanVar(value=CONFIG.skip_night)
        skip_check = ttk.Checkbutton(frame, text="夜间暂停刷新", variable=skip_var)
        skip_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=10)

        ttk.Label(frame, text="夜间开始时间:").grid(row=1, column=0, sticky="w", pady=5)
        start_var = tk.IntVar(value=CONFIG.night_start)
        start_spin = ttk.Spinbox(frame, from_=0, to=23, textvariable=start_var, width=10)
        start_spin.grid(row=1, column=1, padx=20, pady=5, sticky="w")

        ttk.Label(frame, text="夜间结束时间:").grid(row=2, column=0, sticky="w", pady=5)
        end_var = tk.IntVar(value=CONFIG.night_end)
        end_spin = ttk.Spinbox(frame, from_=0, to=23, textvariable=end_var, width=10)
        end_spin.grid(row=2, column=1, padx=20, pady=5, sticky="w")

        ttk.Label(frame, text="例如: 23:00 - 7:00", foreground="gray").grid(row=3, column=1, sticky="w", padx=20, pady=5)

        self.widgets["night.skip_night"] = skip_var
        self.widgets["night.night_start"] = start_var
        self.widgets["night.night_end"] = end_var

    def create_weather_tab(self):
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="天气配置")

        ttk.Label(frame, text="天气 API Key:", font=("Helvetica", 11)).grid(row=0, column=0, sticky="w", pady=10)
        key_var = tk.StringVar(value=CONFIG.weather_key)
        key_entry = ttk.Entry(frame, textvariable=key_var, width=35)
        key_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")

        api_tip = tk.Label(
            frame,
            text="申请 Key（点击跳转到和风天气开发文档）",
            foreground="blue",
            cursor="hand2",
            font=("Helvetica", 11, "underline")
        )
        api_tip.grid(row=1, column=1, sticky="w", padx=20, pady=(0, 10))
        api_tip.bind("<Button-1>", lambda e: self.open_url("https://dev.qweather.com/docs/configuration/project-and-key/"))

        ttk.Label(frame, text="城市 / Location:", font=("Helvetica", 11)).grid(row=2, column=0, sticky="w", pady=10)
        loc_var = tk.StringVar(value=CONFIG.location)
        loc_entry = ttk.Entry(frame, textvariable=loc_var, width=35)
        loc_entry.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        loc_tip = tk.Label(
            frame,
            text="查看中国城市列表（CSV，点击跳转）",
            foreground="blue",
            cursor="hand2",
            font=("Helvetica", 11, "underline")
        )
        loc_tip.grid(row=3, column=1, sticky="w", padx=20, pady=(0, 5))
        loc_tip.bind("<Button-1>", lambda e: self.open_url("https://github.com/qwd/LocationList/blob/master/China-City-List-latest.csv"))

        ttk.Label(
            frame,
            text="城市ID（如 101010100）",
            foreground="gray",
            font=("Helvetica", 11)
        ).grid(row=4, column=1, sticky="w", padx=20, pady=5)

        self.widgets["weather.key"] = key_var
        self.widgets["weather.location"] = loc_var

    def create_mail_tab(self):
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="邮件通知")

        enabled_var = tk.BooleanVar(value=CONFIG.mail_enabled)
        enabled_check = ttk.Checkbutton(frame, text="启用邮件通知", variable=enabled_var, state="disabled")
        enabled_check.grid(row=0, column=0, sticky="w", pady=10)

        ttk.Label(frame, text="天气刷新后发送邮件通知（暂不支持）", foreground="gray").grid(row=1, column=0, sticky="w", pady=5)

        self.widgets["mail.enabled"] = enabled_var

    def save_config(self):
        """保存所有配置"""
        try:
            CONFIG.set("refresh", "interval_minutes", self.widgets["refresh.interval_minutes"].get())
            CONFIG.set("refresh", "force_refresh_at_midnight", self.widgets["refresh.force_refresh_at_midnight"].get())

            CONFIG.set("night", "skip_night", self.widgets["night.skip_night"].get())
            CONFIG.set("night", "night_start", self.widgets["night.night_start"].get())
            CONFIG.set("night", "night_end", self.widgets["night.night_end"].get())

            CONFIG.set("weather", "key", self.widgets["weather.key"].get())
            CONFIG.set("weather", "location", self.widgets["weather.location"].get())

            CONFIG.set("mail", "enabled", self.widgets["mail.enabled"].get())

            from app.state_file import set_config_changed
            set_config_changed(True)

            remove_lock()
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败:\n{e}")
            remove_lock()

    def cancel(self):
        remove_lock()
        self.root.destroy()

    def open_url(self, url: str):
        try:
            webbrowser.open(url, new=2)
        except Exception as ex:
            messagebox.showerror("无法打开链接", f"开启浏览器失败：\n{ex}")

# ================== 主程序 ==================
def main():
    existing_pid = is_gui_running()
    if existing_pid:
        activate_existing_gui(existing_pid)
        sys.exit(0)

    write_lock()

    root = tk.Tk()
    root.withdraw()
    root.title("UpdateWeather 配置")
    root.resizable(False, False)

    width, height = 580, 420
    center_window(root, width, height)

    ConfigGUI(root)

    root.deiconify()
    root.lift()
    root.focus_force()

    def on_close():
        remove_lock()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()


def launch_gui_process():
    existing_pid = is_gui_running()
    if existing_pid:
        activate_existing_gui(existing_pid)
        return

    from pathlib import Path
    root_dir = Path(__file__).resolve().parent.parent  # gui_process.py → app → root

    gui_script = root_dir / "app" / "gui_process.py"

    # ✅ 关键修复：使用 -m 参数 + 模块名
    # 而不是直接传文件路径
    # 这样 Python 会正确识别 if __name__ == "__main__" 块
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root_dir) + os.pathsep + env.get("PYTHONPATH", "")

    print(f"[Launch GUI] 启动独立 GUI 进程")
    print(f"  可执行文件: {sys.executable}")
    print(f"  GUI 脚本: {gui_script}")
    print(f"  工作目录: {root_dir}")

    try:
        # ✅ 改用 -m app.gui_process 方式启动
        # 这样会执行 if __name__ == "__main__" 块中的代码
        subprocess.Popen(
            [sys.executable, "-m", "app.gui_process"],
            cwd=str(root_dir),
            env=env,
            start_new_session=True,
        )
        print("[Launch GUI] GUI 进程启动成功")
    except Exception as e:
        print(f"[Launch GUI] 启动 GUI 进程失败: {e}")


if __name__ == "__main__":
    main()