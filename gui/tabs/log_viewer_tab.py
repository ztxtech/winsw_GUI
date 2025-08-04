import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox


class LogViewerTab(ttk.Frame):
    """ 内嵌的日志查看器选项卡 """

    def __init__(self, parent):
        super().__init__(parent)
        self.log_paths = {}
        self.log_texts = {}
        self.last_positions = {}
        self.after_id = None
        self.current_config = None  # 保存当前服务的配置
        self.create_widgets()

    def create_widgets(self):
        # 顶部框架，用于放置按钮
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=5, pady=(5, 0))

        clear_button = ttk.Button(top_frame, text="清除当前服务日志", command=self.clear_logs)
        clear_button.pack(side="left")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)

        log_types = {"Wrapper": "wrapper.log", "Output": "out.log", "Error": "err.log"}
        for name, suffix in log_types.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)

            text_widget = tk.Text(frame, wrap="none", state="disabled", font=("Courier New", 9))
            v_scroll = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
            h_scroll = ttk.Scrollbar(frame, orient="horizontal", command=text_widget.xview)
            text_widget.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

            v_scroll.pack(side="right", fill="y")
            h_scroll.pack(side="bottom", fill="x")
            text_widget.pack(side="left", expand=True, fill="both")

            self.log_texts[suffix] = text_widget
            self.last_positions[suffix] = 0

    def clear_logs(self):
        """清除当前选中服务的所有日志文件"""
        if not self.current_config or not self.log_paths:
            messagebox.showwarning("操作无效", "请先选择一个服务。")
            return

        service_id = self.current_config.get('id', '未知服务')
        if not messagebox.askyesno("确认清除", f"你确定要删除服务 '{service_id}' 的所有日志文件吗？\n此操作不可恢复。"):
            return

        # 停止监控，避免文件占用
        self.stop_monitoring()

        cleared_files = []
        errors = []
        for file_path in self.log_paths.values():
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    cleared_files.append(os.path.basename(file_path))
                except OSError as e:
                    errors.append(f"删除 {os.path.basename(file_path)} 失败: {e}")

        # 清空UI显示
        self._clear_all_logs()

        # 显示结果
        if errors:
            messagebox.showerror("清除失败", "\n".join(errors))
        elif cleared_files:
            messagebox.showinfo("成功", f"以下日志文件已清除:\n\n" + "\n".join(cleared_files))
        else:
            messagebox.showinfo("完成", "没有找到需要清除的日志文件。")

        # 重新开始监控
        self.start_monitoring(self.current_config)

    def start_monitoring(self, config: dict):
        self.stop_monitoring()  # 先停止上一个监控
        self.current_config = config  # 保存当前配置
        self._determine_log_paths(config)
        self._clear_all_logs()
        self.log_to_all("--- 开始监控日志 ---\n")
        self.update_logs()

    def stop_monitoring(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.log_to_all("\n--- 停止监控日志 ---\n")
        self.after_id = None

    def _determine_log_paths(self, config: dict):
        service_id = config.get('id')
        if not service_id:
            self.log_paths = {}
            return

        log_dir = config.get('logpath')
        if not log_dir or not os.path.isdir(log_dir):
            base_deploy_dir = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "deploy")
            log_dir = os.path.join(base_deploy_dir, service_id)

        self.log_paths = {
            "wrapper.log": os.path.join(log_dir, f"{service_id}.wrapper.log"),
            "out.log": os.path.join(log_dir, f"{service_id}.out.log"),
            "err.log": os.path.join(log_dir, f"{service_id}.err.log"),
        }
        self.last_positions = {key: 0 for key in self.log_paths}

    def update_logs(self):
        for suffix, path in self.log_paths.items():
            try:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        if os.path.getsize(path) < self.last_positions[suffix]:
                            self.last_positions[suffix] = 0  # 日志文件被重置

                        f.seek(self.last_positions[suffix])
                        new_content = f.read()
                        if new_content:
                            self._log_message(suffix, new_content)
                        self.last_positions[suffix] = f.tell()
            except Exception:
                pass  # 静默处理读取错误

        self.after_id = self.after(1000, self.update_logs)

    def _clear_all_logs(self):
        for text_widget in self.log_texts.values():
            text_widget.config(state="normal")
            text_widget.delete("1.0", tk.END)
            text_widget.config(state="disabled")

    def log_to_all(self, message):
        for suffix in self.log_texts.keys():
            self._log_message(suffix, message)

    def _log_message(self, suffix, message):
        text_widget = self.log_texts.get(suffix)
        if text_widget:
            text_widget.config(state="normal")
            text_widget.insert(tk.END, message)
            text_widget.see(tk.END)
            text_widget.config(state="disabled")
