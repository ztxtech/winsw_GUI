import ctypes
import os
import sys
import tkinter as tk

from core.settings_manager import SettingsManager
from gui.main_window import MainWindow


# --- 新增的函数 ---
def resource_path(relative_path):
    """ 获取资源的绝对路径，无论是开发环境还是PyInstaller打包后 """
    try:
        # PyInstaller 创建一个临时文件夹，并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base_path, relative_path)


# 确保我们的自定义模块可以被导入
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


class App:
    """
    应用程序主类，负责初始化和运行整个程序。
    """
    __version__ = "Preview 0.0.1"

    def __init__(self, root):
        self.root = root
        self.root.title(f"WinSW 图形化管理工具 by ztxtech ({self.__version__})")

        self.setup_directories()
        self.set_app_icon()

        self.settings_manager = SettingsManager()
        self.root.geometry(self.settings_manager.get('window_geometry'))

        self.main_window = MainWindow(self.root, self.settings_manager, self.__version__)
        self.main_window.pack(expand=True, fill="both")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_app_icon(self):
        """设置应用程序的图标。"""
        try:
            # --- 使用新的 resource_path 函数 ---
            icon_path = resource_path(os.path.join('etc', 'icon', 'ztxtech.png'))

            if os.path.exists(icon_path):
                photo = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, photo)
                print(f"成功加载图标: {icon_path}")
            else:
                print(f"警告: 图标文件未找到，请将其放置在: {icon_path}")
        except tk.TclError as e:
            print(f"错误: 加载图标失败，请确保 'ztxtech.png' 是有效的PNG图片。错误信息: {e}")
        except Exception as e:
            print(f"发生未知错误，加载图标失败: {e}")

    def on_closing(self):
        """在窗口关闭前保存状态。"""
        self.main_window.save_current_settings()
        self.root.destroy()

    def setup_directories(self):
        """创建程序所需的核心工作目录。"""
        # 只创建运行时需要生成的目录
        for dir_name in ["bin", "services", "logs"]:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)


def set_dpi_awareness():
    """设置Windows DPI感知，确保在高分屏上界面清晰。"""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        print("DPI Awareness 设置为 Per-Monitor V2")
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
            print("DPI Awareness 设置为 System Aware")
        except (AttributeError, OSError):
            print("警告: 无法设置 DPI 感知。")


if __name__ == "__main__":
    set_dpi_awareness()

    root = tk.Tk()
    app = App(root)
    root.mainloop()
