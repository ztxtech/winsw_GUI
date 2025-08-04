import json
import os
import subprocess
import sys

import requests


class WinSWManager:
    """
    负责下载WinSW、部署服务以及执行所有服务控制命令。
    采用全局WinSW.exe管理模式。
    """

    def __init__(self, log_callback, settings_manager):
        self.log = log_callback
        self.settings_manager = settings_manager
        self.base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        self.bin_dir = os.path.join(self.base_dir, "bin")
        self.managed_winsw_path = os.path.join(self.bin_dir, "winsw-x64.exe")
        self.github_api_url = "https://api.github.com/repos/winsw/winsw/releases"
        self.target_asset_name = "WinSW-x64.exe"

        os.makedirs(self.bin_dir, exist_ok=True)

    def _get_latest_winsw_download_url(self):
        """通过GitHub API获取最新的WinSW v3.x x64下载链接。"""
        self.log(f"正在从GitHub API获取所有版本信息以查找最新的v3.x...")
        try:
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()
            all_releases_data = response.json()

            for release in all_releases_data:
                tag_name = release.get("tag_name", "")
                if tag_name.lower().startswith("v3"):
                    self.log(f"找到最新的v3版本: {tag_name}")
                    for asset in release.get("assets", []):
                        asset_name_lower = asset.get("name", "").lower()
                        if "winsw" in asset_name_lower and ".exe" in asset_name_lower and (
                                "x64" in asset_name_lower or "amd64" in asset_name_lower):
                            download_url = asset.get("browser_download_url")
                            found_asset_name = asset.get("name")
                            self.log(f"成功找到匹配的64位可执行文件 '{found_asset_name}'。")
                            return download_url
                    self.log(f"警告: 在版本 {tag_name} 中未找到任何64位可执行文件，继续查找下一个版本...")
                    continue
            self.log(f"错误: 在所有版本中均未找到任何有效的v3.x版本及64位可执行文件。")
            return None
        except requests.exceptions.RequestException as e:
            self.log(f"错误: 请求GitHub API失败。{e}")
            return None
        except json.JSONDecodeError:
            self.log("错误: 解析GitHub API响应失败。")
            return None

    def get_winsw_path(self):
        """根据设置获取有效的WinSW.exe路径，如果需要则下载。"""
        mode = self.settings_manager.get('winsw_management_mode')

        if mode == 'custom':
            custom_path = self.settings_manager.get('winsw_custom_path')
            if os.path.exists(custom_path):
                return custom_path
            else:
                self.log(f"错误: 自定义WinSW路径无效: {custom_path}")
                return None

        if not os.path.exists(self.managed_winsw_path):
            download_url = self._get_latest_winsw_download_url()
            if not download_url:
                self.log("无法获取下载链接，请检查网络或稍后重试。")
                return None

            self.log(f"WinSW executable not found. Downloading from {download_url}...")
            try:
                with requests.get(download_url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    with open(self.managed_winsw_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                self.log(f"WinSW downloaded successfully to '{self.managed_winsw_path}'.")
            except requests.exceptions.RequestException as e:
                self.log(f"错误: 下载WinSW失败。{e}")
                return None

        return self.managed_winsw_path

    def _run_command(self, command_parts: list):
        """运行WinSW命令并返回输出。"""
        try:
            self.log(f"正在运行命令: '{' '.join(command_parts)}'")
            result = subprocess.run(
                command_parts, capture_output=True, text=True,
                check=False, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW
            )
            output = result.stdout + result.stderr
            self.log(f"命令输出:\n---\n{output.strip()}\n---")
            return output
        except Exception as e:
            self.log(f"运行命令时出错: {e}")
            return f"Error running command: {e}"

    def _execute(self, command, config):
        """执行命令的统一入口。"""
        # 1. 获取WinSW.exe的路径
        winsw_path = self.get_winsw_path()
        if not winsw_path:
            self.log("错误: 无法找到或下载 WinSW.exe。请检查设置和网络连接。")
            return

        # 2. 获取服务ID和XML文件路径
        service_id = config.get('id')
        if not service_id:
            self.log(f"错误: 服务ID为空，无法执行'{command}'命令。")
            return

        xml_path = os.path.join("services", f"{service_id}.xml")
        # 确保XML文件是绝对路径，以避免相对路径问题
        abs_xml_path = os.path.abspath(xml_path)

        if not os.path.exists(abs_xml_path):
            self.log(f"错误: 找不到配置文件 '{abs_xml_path}'。请先保存配置。")
            return

        # --- 关键修正处 ---
        # 3. 对所有命令，都使用XML文件路径作为参数
        command_parts = [winsw_path, command, abs_xml_path]

        # 4. 执行命令
        return self._run_command(command_parts)

    def install(self, config):
        return self._execute("install", config)

    def uninstall(self, config):
        return self._execute("uninstall", config)

    def start(self, config):
        return self._execute("start", config)

    def stop(self, config):
        return self._execute("stop", config)

    def restart(self, config):
        return self._execute("restart", config)

    def status(self, config):
        return self._execute("status", config)

    def refresh(self, config):
        return self._execute("refresh", config)
