import json
import os


class SettingsManager:
    """
    负责加载和保存应用程序的全局设置 (settings.json)。
    """

    def __init__(self, settings_file='settings.json'):
        self.settings_file = settings_file
        self.settings = self._load_defaults()
        self.load_settings()

    def _load_defaults(self):
        """返回默认设置。"""
        return {
            'winsw_management_mode': 'auto',
            'winsw_custom_path': '',
            'window_geometry': '1200x800+100+100',  # 窗口大小和位置
            'main_sash_pos': 300,  # 主左右分割条位置
            'right_sash_pos': 500  # 右侧上下分割条位置
        }

    def load_settings(self):
        """从settings.json加载设置，如果文件不存在则使用默认值。"""
        if not os.path.exists(self.settings_file):
            self.save_settings()
            return

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                # 确保所有默认键都存在
                for key, value in self._load_defaults().items():
                    self.settings[key] = loaded_settings.get(key, value)
        except (json.JSONDecodeError, IOError) as e:
            print(f"警告: 无法加载 settings.json，将使用默认设置。错误: {e}")
            self.settings = self._load_defaults()

    def save_settings(self):
        """将当前设置保存到settings.json。"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(f"错误: 无法保存设置到 {self.settings_file}。错误: {e}")

    def get(self, key):
        """获取一个设置项的值。"""
        return self.settings.get(key)

    def set(self, key, value):
        """设置一个设置项的值。"""
        self.settings[key] = value
