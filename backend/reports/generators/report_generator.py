import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import sys
import threading
import time

from report_logic import batch_generate_reports


class ReportGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("管理潜质测评报告生成器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f5ff")

        # 设置图标
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass

        # 应用变量
        self.excel_path = ""
        self.output_dir = ""
        self.running = False

        self.create_widgets()
        self.update_status("准备就绪")

        # 将窗口置于屏幕中央
        self.center_window()

    def center_window(self):
        """将窗口置于屏幕中央"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        # 创建主框架
        main_frame = tk.Frame(self.root, bg="#f0f5ff", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_frame = tk.Frame(main_frame, bg="#f0f5ff")
        title_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = tk.Label(
            title_frame,
            text="管理潜质测评报告生成器",
            font=("Arial", 20, "bold"),
            bg="#f0f5ff",
            fg="#2c3e50"
        )
        title_label.pack(side=tk.LEFT)

        # 版本号
        version_label = tk.Label(
            title_frame,
            text="v1.0",
            font=("Arial", 10),
            bg="#f0f5ff",
            fg="#7f8c8d"
        )
        version_label.pack(side=tk.RIGHT, padx=10)

        # 功能卡片
        self.create_file_selection_card(main_frame)
        self.create_progress_section(main_frame)
        self.create_actions_section(main_frame)
        self.create_log_section(main_frame)

        # 状态栏
        self.create_status_bar()

    def create_file_selection_card(self, parent):
        """创建文件选择卡片"""
        card_frame = tk.LabelFrame(
            parent,
            text="文件设置",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#3498db",
            padx=20,
            pady=15,
            relief=tk.FLAT,
            highlightbackground="#e0e7ff",
            highlightthickness=2
        )
        card_frame.pack(fill=tk.X, padx=5, pady=(0, 20))
        card_frame.grid_columnconfigure(1, weight=1)

        # Excel文件选择
        excel_frame = tk.Frame(card_frame, bg="#ffffff")
        excel_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=5)
        excel_frame.columnconfigure(1, weight=1)

        tk.Label(
            excel_frame,
            text="Excel数据文件:",
            bg="#ffffff",
            font=("Arial", 10)
        ).grid(row=0, column=0, sticky="w")

        self.excel_entry = tk.Entry(
            excel_frame,
            width=40,
            font=("Arial", 10),
            state="readonly",
            readonlybackground="#f8f9fa",
            relief=tk.SOLID,
            borderwidth=1,
            highlightbackground="#e0e7ff",
            highlightthickness=1
        )
        self.excel_entry.grid(row=0, column=1, padx=10, sticky="ew")

        browse_excel_btn = tk.Button(
            excel_frame,
            text="浏览...",
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            command=self.select_excel_file
        )
        browse_excel_btn.grid(row=0, column=2, padx=(5, 0))

        # 输出目录选择
        output_frame = tk.Frame(card_frame, bg="#ffffff")
        output_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        output_frame.columnconfigure(1, weight=1)

        tk.Label(
            output_frame,
            text="输出目录:",
            bg="#ffffff",
            font=("Arial", 10)
        ).grid(row=0, column=0, sticky="w")

        self.output_entry = tk.Entry(
            output_frame,
            width=40,
            font=("Arial", 10),
            state="readonly",
            readonlybackground="#f8f9fa",
            relief=tk.SOLID,
            borderwidth=1,
            highlightbackground="#e0e7ff",
            highlightthickness=1
        )
        self.output_entry.grid(row=0, column=1, padx=10, sticky="ew")

        browse_output_btn = tk.Button(
            output_frame,
            text="浏览...",
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            command=self.select_output_dir
        )
        browse_output_btn.grid(row=0, column=2, padx=(5, 0))

        # 分隔线
        separator = ttk.Separator(card_frame, orient=tk.HORIZONTAL)
        separator.grid(row=2, column=0, columnspan=3, pady=15, sticky="ew")

        # 设置说明
        info_label = tk.Label(
            card_frame,
            text="请选择包含人才测评数据的Excel文件和输出目录。系统将自动生成报告PDF文件。",
            font=("Arial", 9),
            bg="#ffffff",
            fg="#7f8c8d",
            justify=tk.LEFT
        )
        info_label.grid(row=3, column=0, columnspan=3, sticky="w")

    def create_progress_section(self, parent):
        """创建进度显示部分"""
        progress_frame = tk.LabelFrame(
            parent,
            text="报告生成进度",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#3498db",
            padx=20,
            pady=15,
            relief=tk.FLAT,
            highlightbackground="#e0e7ff",
            highlightthickness=2
        )
        progress_frame.pack(fill=tk.X, padx=5, pady=(0, 20))

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
            length=750
        )
        self.progress_bar.pack(pady=10)

        # 进度信息
        progress_info_frame = tk.Frame(progress_frame, bg="#ffffff")
        progress_info_frame.pack(fill=tk.X, pady=5)

        self.progress_label = tk.Label(
            progress_info_frame,
            text="准备开始...",
            font=("Arial", 10),
            bg="#ffffff",
            fg="#2c3e50",
            anchor=tk.W
        )
        self.progress_label.pack(side=tk.LEFT, fill=tk.X)

        self.progress_percentage = tk.Label(
            progress_info_frame,
            text="0%",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#3498db",
            anchor=tk.E
        )
        self.progress_percentage.pack(side=tk.RIGHT)

    def create_actions_section(self, parent):
        """创建操作按钮区域"""
        actions_frame = tk.Frame(parent, bg="#f0f5ff")
        actions_frame.pack(fill=tk.X, padx=5, pady=10)

        # 开始按钮
        self.start_btn = tk.Button(
            actions_frame,
            text="开始生成报告",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            width=20,
            height=2,
            relief=tk.FLAT,
            command=self.start_generation
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # 打开输出目录按钮 - 现在默认启用
        self.open_output_btn = tk.Button(
            actions_frame,
            text="打开输出目录",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            width=15,
            relief=tk.FLAT,
            command=self.open_output_dir
        )
        self.open_output_btn.pack(side=tk.RIGHT, padx=5)

        # 取消按钮
        self.cancel_btn = tk.Button(
            actions_frame,
            text="取消",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            width=15,
            relief=tk.FLAT,
            command=self.cancel_generation,
            state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)

    # def create_actions_section(self, parent):
    #     """创建操作按钮区域"""
    #     actions_frame = tk.Frame(parent, bg="#f0f5ff")
    #     actions_frame.pack(fill=tk.X, padx=5, pady=10)
    #
    #     # 开始按钮
    #     self.start_btn = tk.Button(
    #         actions_frame,
    #         text="开始生成报告",
    #         font=("Arial", 10, "bold"),
    #         bg="#27ae60",
    #         fg="white",
    #         width=20,
    #         height=2,
    #         relief=tk.FLAT,
    #         command=self.start_generation
    #     )
    #     self.start_btn.pack(side=tk.LEFT, padx=5)
    #
    #     # 打开输出目录按钮
    #     self.open_output_btn = tk.Button(
    #         actions_frame,
    #         text="打开输出目录",
    #         font=("Arial", 10),
    #         bg="#3498db",
    #         fg="white",
    #         width=15,
    #         relief=tk.FLAT,
    #         command=self.open_output_dir,
    #         state=tk.DISABLED
    #     )
    #     self.open_output_btn.pack(side=tk.RIGHT, padx=5)
    #
    #     # 取消按钮
    #     self.cancel_btn = tk.Button(
    #         actions_frame,
    #         text="取消",
    #         font=("Arial", 10),
    #         bg="#e74c3c",
    #         fg="white",
    #         width=15,
    #         relief=tk.FLAT,
    #         command=self.cancel_generation,
    #         state=tk.DISABLED
    #     )
    #     self.cancel_btn.pack(side=tk.RIGHT, padx=5)

    def create_log_section(self, parent):
        """创建日志显示区域"""
        log_frame = tk.LabelFrame(
            parent,
            text="操作日志",
            font=("Arial", 10, "bold"),
            bg="#ffffff",
            fg="#3498db",
            padx=20,
            pady=15,
            relief=tk.FLAT,
            highlightbackground="#e0e7ff",
            highlightthickness=2
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 20))

        # 日志文本区域
        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Arial", 9),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            height=8
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = tk.Label(
            self.root,
            text="准备就绪",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#e0e7ff",
            fg="#2c3e50",
            font=("Arial", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        """更新状态栏消息"""
        self.status_bar.config(text=message)
        self.status_bar.update_idletasks()

    def update_progress(self, value, message):
        """更新进度条和消息"""
        self.progress_var.set(value)
        self.progress_percentage.config(text=f"{int(value)}%")
        self.progress_label.config(text=message)
        self.root.update_idletasks()

    def log_message(self, message):
        """添加日志消息"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)  # 滚动到底部
        self.log_text.update_idletasks()

    def select_excel_file(self):
        """选择Excel文件"""
        file_path = filedialog.askopenfilename(
            title="选择Excel数据文件",
            filetypes=[("Excel文件", "*.xlsx;*.xls")]
        )
        if file_path:
            self.excel_path = file_path
            self.excel_entry.config(state="normal")
            self.excel_entry.delete(0, tk.END)
            self.excel_entry.insert(0, file_path)
            self.excel_entry.config(state="readonly")

            # 自动设置输出目录为Excel文件所在目录
            output_dir = os.path.dirname(file_path)
            if os.path.exists(output_dir):
                self.output_dir = os.path.join(output_dir, "测评报告")
                self.output_entry.config(state="normal")
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, self.output_dir)
                self.output_entry.config(state="readonly")

                # 尝试创建输出目录
                try:
                    os.makedirs(self.output_dir, exist_ok=True)
                except Exception as e:
                    self.log_message(f"无法创建输出目录: {str(e)}")

    def select_output_dir(self):
        """选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择报告输出目录")
        if dir_path:
            self.output_dir = dir_path
            self.output_entry.config(state="normal")
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, dir_path)
            self.output_entry.config(state="readonly")

            # 尝试创建目录
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception as e:
                self.log_message(f"无法创建输出目录: {str(e)}")

    def start_generation(self):
        """开始生成报告"""
        if not self.excel_path:
            messagebox.showerror("错误", "请选择Excel数据文件")
            return

        if not self.output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return

        # 检查文件是否存在
        if not os.path.isfile(self.excel_path):
            messagebox.showerror("错误", f"文件不存在: {self.excel_path}")
            return

        # 检查输出目录可写
        if not os.access(self.output_dir, os.W_OK):
            messagebox.showerror("错误", f"输出目录不可写: {self.output_dir}")
            return

        # 更新UI状态
        self.running = True
        self.start_btn.config(state=tk.DISABLED, bg="#95a5a6")
        self.cancel_btn.config(state=tk.NORMAL)
        self.open_output_btn.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)  # 清空日志
        self.update_progress(0, "开始处理...")
        self.log_message(f"开始生成报告...")
        self.log_message(f"Excel文件: {self.excel_path}")
        self.log_message(f"输出目录: {self.output_dir}")

        # 在后台线程中运行报告生成
        threading.Thread(target=self.run_generation, daemon=True).start()

    def run_generation(self):
        """执行报告生成任务"""
        try:
            # 获取应用程序基础目录
            if getattr(sys, 'frozen', False):
                # 打包后的应用程序
                base_dir = os.path.dirname(sys.executable)
            else:
                # 脚本运行模式
                base_dir = os.path.dirname(os.path.abspath(__file__))

            # 调用核心逻辑 - 传入base_dir
            batch_generate_reports(
                self.excel_path,
                self.output_dir,
                self.progress_callback,
                self.log_callback,
                base_dir=base_dir
            )

            # 报告生成完成后更新UI
            self.log_message("\n所有报告生成完成！")
            self.update_progress(100, "报告生成完成")
            self.log_message(f"输出目录: {self.output_dir}")

            # 始终确保打开目录按钮可用
            self.open_output_btn.config(state=tk.NORMAL)
        except Exception as e:
            # ... 错误处理代码 ...

            # 始终确保打开目录按钮可用
            self.open_output_btn.config(state=tk.NORMAL)

        finally:
            # 恢复UI状态
            self.running = False
            self.start_btn.config(state=tk.NORMAL, bg="#27ae60")
            self.cancel_btn.config(state=tk.DISABLED)
            self.open_output_btn.config(state=tk.NORMAL)

    # def run_generation(self):
    #     """执行报告生成任务"""
    #     try:
    #         # 获取应用程序基础目录
    #         if getattr(sys, 'frozen', False):
    #             # 打包后的应用程序
    #             base_dir = os.path.dirname(sys.executable)
    #         else:
    #             # 脚本运行模式
    #             base_dir = os.path.dirname(os.path.abspath(__file__))
    #
    #         # 调用核心逻辑 - 传入base_dir
    #         batch_generate_reports(
    #             self.excel_path,
    #             self.output_dir,
    #             self.progress_callback,
    #             self.log_callback,
    #             base_dir=base_dir
    #         )
    #
    #         # 报告生成完成后更新UI
    #         self.log_message("\n所有报告生成完成！")
    #         self.update_progress(100, "报告生成完成")
    #         self.log_message(f"输出目录: {self.output_dir}")
    #
    #     except Exception as e:
    #         self.log_message(f"\n报告生成失败: {str(e)}")
    #         self.update_progress(0, f"生成失败: {str(e)}")
    #         messagebox.showerror("错误", f"报告生成失败: {str(e)}")
    #
    #     finally:
    #         # 恢复UI状态
    #         self.running = False
    #         self.start_btn.config(state=tk.NORMAL, bg="#27ae60")
    #         self.cancel_btn.config(state=tk.DISABLED)
    #         self.open_output_btn.config(state=tk.NORMAL)

    def progress_callback(self, progress, message):
        """报告生成的进度回调函数"""
        if not self.running:  # 如果用户取消了生成任务
            return False

        self.update_progress(progress, message)
        return True  # 继续执行

    def log_callback(self, message):
        """日志回调函数"""
        self.log_message(message)

    def cancel_generation(self):
        """取消报告生成"""
        self.running = False
        self.log_message("\n报告生成已取消")
        self.update_progress(0, "已取消")
        self.start_btn.config(state=tk.NORMAL, bg="#27ae60")
        self.cancel_btn.config(state=tk.DISABLED)

    def open_output_dir(self):
        """打开输出目录 - 兼容所有操作系统"""
        if not self.output_dir or not os.path.isdir(self.output_dir):
            # 创建目录（如果需要）
            try:
                os.makedirs(self.output_dir, exist_ok=True)
            except Exception:
                self.log_message(f"无法创建目录: {self.output_dir}")
                messagebox.showerror("错误", f"目录不存在且无法创建: {self.output_dir}")
                return

            # 再次检查
            if not os.path.isdir(self.output_dir):
                self.log_message(f"目录不存在: {self.output_dir}")
                messagebox.showerror("错误", f"目录不存在: {self.output_dir}")
                return

        try:
            # 平台无关的安全路径处理
            output_path = os.path.normpath(self.output_dir)

            self.log_message(f"尝试打开目录: {output_path}")

            # Windows
            if sys.platform == "win32":
                os.startfile(output_path)
                self.log_message("使用os.startfile成功")

            # macOS
            elif sys.platform == "darwin":
                import subprocess
                subprocess.run(["open", output_path])
                self.log_message("使用open命令成功")

            # Linux及其他
            else:
                try:
                    # 尝试使用文件管理器
                    import subprocess
                    subprocess.run(["xdg-open", output_path])
                    self.log_message("使用xdg-open成功")
                except Exception:
                    # 回退到浏览器方式
                    try:
                        import webbrowser
                        webbrowser.open(f"file://{output_path}")
                        self.log_message("使用webbrowser.open成功")
                    except Exception:
                        # 最后尝试 - 通用Linux命令
                        os.system(f'nautilus "{output_path}"')
                        self.log_message("使用nautilus尝试")

        except Exception as e:
            error_msg = f"无法打开目录: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("错误", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = ReportGeneratorApp(root)
    root.mainloop()