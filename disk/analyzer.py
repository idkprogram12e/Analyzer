import os, sys, shutil, threading, winreg, platform, psutil, tkinter as tk
from tkinter import filedialog, messagebox, ttk
LEXICON = {
    "ru": {
        "title": "DiskAccuracy v1.0", "tab_scan": "🔍 Очистка Диска", "tab_cache": "⚡ Экспресс-Кэш", "tab_installers": "📦 Установщики (>1 Гб)", "tab_fix": "🛠️ Фантомные Игры", "tab_hardware": "🖥️ Комплектующие", "tab_taskmgr": "📈 Диспетчер задач",
        "lbl_path": "Выберите путь для анализа:", "btn_browse": "Обзор...", "btn_scan": "Глубокий анализ", "btn_del": "Удалить папку", "btn_express": "Очистить кэш (Телега/Temp)",
        "btn_scan_inst": "Найти забытые установщики", "btn_del_inst": "Удалить файл установщика", "btn_update_reg": "🔄 Обновить список", "btn_fix_reg": "❌ Стереть запись из реестра",
        "hw_title": "Спецификация железа:", "hw_scan": "Проверить здоровье комплектующих", "tm_title": "Мониторинг нагрузки live:", "confirm_del": "Вы уверены, что хотите НАВСЕГДА удалить эту локацию?", "success": "Успешно!", "cache_cleaned": "Экспресс-кэш успешно очищен!"
    },
    "en": {
        "title": "DiskAccuracy v1.0", "tab_scan": "🔍 Disk Cleanup", "tab_cache": "⚡ Express Cache", "tab_installers": "📦 Installers (>1 GB)", "tab_fix": "🛠️ Phantom Games", "tab_hardware": "🖥️ Hardware Info", "tab_taskmgr": "📈 Task Manager",
        "lbl_path": "Select path for analysis:", "btn_browse": "Browse...", "btn_scan": "Deep Analysis", "btn_del": "Delete Folder", "btn_express": "Clear Cache (TG/Temp)",
        "btn_scan_inst": "Find Forgotten Installers", "btn_del_inst": "Delete Installer File", "btn_update_reg": "🔄 Refresh App List", "btn_fix_reg": "❌ Remove Registry Entry",
        "hw_title": "Your PC Hardware Specification:", "hw_scan": "Check Hardware Health Status", "tm_title": "Real-time System Load Monitoring:", "confirm_del": "Are you sure you want to PERMANENTLY delete this location?", "success": "Success!", "cache_cleaned": "Express cache has been successfully cleared!"
    }
}
class DiskAccuracyApp(tk.Tk):
    def __init__(self):
        super().__init__(); self.current_lang = "ru"; self.selected_path = tk.StringVar(); self.geometry("950x680"); self.minsize(800, 550)
        lf = tk.Frame(self, bd=1, relief=tk.RAISED, pady=5); lf.pack(fill=tk.X); tk.Label(lf, text="Language / Язык:").pack(side=tk.LEFT, padx=10)
        self.lang_box = ttk.Combobox(lf, values=["Русский", "English"], state="readonly", width=12); self.lang_box.set("Русский"); self.lang_box.pack(side=tk.LEFT, padx=5); self.lang_box.bind("<<ComboboxSelected>>", lambda e: self.on_lang_change())
        self.tabs = ttk.Notebook(self); self.tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tab_scan = tk.Frame(self.tabs, padx=10, pady=10); self.tab_cache = tk.Frame(self.tabs, padx=10, pady=10); self.tab_installers = tk.Frame(self.tabs, padx=10, pady=10); self.tab_fix = tk.Frame(self.tabs, padx=10, pady=10); self.tab_hardware = tk.Frame(self.tabs, padx=10, pady=10); self.tab_taskmgr = tk.Frame(self.tabs, padx=10, pady=10)
        self.tabs.add(self.tab_scan); self.tabs.add(self.tab_cache); self.tabs.add(self.tab_installers); self.tabs.add(self.tab_fix); self.tabs.add(self.tab_hardware); self.tabs.add(self.tab_taskmgr)
        self.build_scan_tab(); self.build_cache_tab(); self.build_installers_tab(); self.build_fix_tab(); self.build_hardware_tab(); self.build_taskmgr_tab(); self.update_language(); self.update_task_manager()
    def on_lang_change(self): self.current_lang = "ru" if self.lang_box.get() == "Русский" else "en"; self.update_language()
    def update_language(self):
        lex = LEXICON[self.current_lang]; self.title(lex["title"])
        for i, m in enumerate(["tab_scan", "tab_cache", "tab_installers", "tab_fix", "tab_hardware", "tab_taskmgr"]): self.tabs.tab(i, text=lex[m])
        self.lbl_p.config(text=lex["lbl_path"]); self.btn_b.config(text=lex["btn_browse"]); self.btn_s.config(text=lex["btn_scan"]); self.btn_d.config(text=lex["btn_del"]); self.btn_exp.config(text=lex["btn_express"])
        self.btn_s_inst.config(text=lex["btn_scan_inst"]); self.btn_d_inst.config(text=lex["btn_del_inst"]); self.btn_u_reg.config(text=lex["btn_update_reg"]); self.btn_f_reg.config(text=lex["btn_fix_reg"]); self.lbl_hw_title.config(text=lex["hw_title"]); self.btn_hw_health.config(text=lex["hw_scan"]); self.lbl_tm_title.config(text=lex["tm_title"])
    def build_scan_tab(self):
        self.lbl_p = tk.Label(self.tab_scan, text="Path:"); self.lbl_p.pack(anchor=tk.W); f1 = tk.Frame(self.tab_scan); f1.pack(fill=tk.X, pady=5)
        self.entry = tk.Entry(f1, textvariable=self.selected_path); self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10)); self.btn_b = tk.Button(f1, text="Browse", command=self.browse); self.btn_b.pack(side=tk.RIGHT)
        f2 = tk.Frame(self.tab_scan); f2.pack(fill=tk.X, pady=10); self.btn_s = tk.Button(f2, text="Scan", width=25, height=2, bg="#dcdcdc", command=self.start_scan); self.btn_s.pack(side=tk.LEFT, padx=(0,10)); self.btn_d = tk.Button(f2, text="Delete", width=20, height=2, command=self.delete_folder); self.btn_d.pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(self.tab_scan, mode='indeterminate'); self.tree = ttk.Treeview(self.tab_scan, columns=("size", "path"), show="headings"); self.tree.heading("size", text="Size"); self.tree.heading("path", text="Path"); self.tree.pack(fill=tk.BOTH, expand=True, pady=5); self.tree.bind("<Double-1>", lambda e: os.startfile(self.tree.item(self.tree.selection(), "values")) if self.tree.selection() else None)
    def browse(self):
        f = filedialog.askdirectory()
        if f: self.selected_path.set(os.path.normpath(f))
    def start_scan(self):
        p = self.selected_path.get().strip()
        if not p or not os.path.exists(p): return
        self.progress.pack(fill=tk.X, padx=10, pady=5); self.progress.start(15); [self.tree.delete(i) for i in self.tree.get_children()]; threading.Thread(target=self.run_scan, args=(p,), daemon=True).start()
    def run_scan(self, path):
        sizes = {}
        for r, d, files in os.walk(path):
            if any(s in r for s in ["Windows\\WinSxS", "Windows\\servicing"]): continue
            try:
                sz = sum(os.path.getsize(os.path.join(r, f)) for f in files if os.path.exists(os.path.join(r, f)))
                if sz > 150 * 1024 * 1024: sizes[os.path.normpath(r)] = sz
            except: continue
        self.after(0, self.end_scan, sorted(sizes.items(), key=lambda x: x, reverse=True))
    def end_scan(self, results):
        for f, sz in results[:50]: gb = sz / (1024**3); readable = f"{gb:.2f} GB" if gb >= 0.1 else f"{sz / (1024**2):.1f} MB"; self.tree.insert("", tk.END, values=(readable, f))
        self.progress.stop(); self.progress.pack_forget()
    def delete_folder(self):
        item = self.tree.selection()
        if item:
            fp = self.tree.item(item, "values")[1]
            if messagebox.askyesno("⚠️ DiskAccuracy", LEXICON[self.current_lang]["confirm_del"] + f"\n\n{fp}"):
                try: shutil.rmtree(fp); self.tree.delete(item)
                except Exception as e: messagebox.showerror("Error", f"Error: {e}")
    def build_cache_tab(self): self.btn_exp = tk.Button(self.tab_cache, text="", font=("Arial", 12, "bold"), width=40, height=3, bg="#ffefdb", command=self.run_express_clean); self.btn_exp.pack(expand=True)
    def run_express_clean(self):
        p = os.environ.get("USERPROFILE")
        for pth in [os.path.join(p, "AppData", "Local", "Temp"), os.path.join(p, "AppData", "Local", "Telegram Desktop", "tdata", "user_data", "cache")]:
            if os.path.exists(pth):
                for item in os.listdir(pth):
                    ip = os.path.join(pth, item)
                    try: shutil.rmtree(ip) if os.path.isdir(ip) else os.remove(ip)
                    except: pass
        messagebox.showinfo("DiskAccuracy", LEXICON[self.current_lang]["cache_cleaned"])
    def build_installers_tab(self):
        f = tk.Frame(self.tab_installers); f.pack(fill=tk.X, pady=5); self.btn_s_inst = tk.Button(f, text="", width=25, command=self.start_installer_scan); self.btn_s_inst.pack(side=tk.LEFT, padx=(0,10)); self.btn_d_inst = tk.Button(f, text="", width=25, command=self.delete_installer_file); self.btn_d_inst.pack(side=tk.LEFT)
        self.inst_progress = ttk.Progressbar(self.tab_installers, mode='indeterminate'); self.inst_tree = ttk.Treeview(self.tab_installers, columns=("size", "name", "path"), show="headings"); self.inst_tree.heading("size", text="Size"); self.inst_tree.heading("name", text="File Name"); self.inst_tree.heading("path", text="Folder"); self.inst_tree.column("size", width=100); self.inst_tree.column("name", width=200); self.inst_tree.pack(fill=tk.BOTH, expand=True, pady=5)
    def start_installer_scan(self):
        p = self.selected_path.get().strip()
        if p and os.path.exists(p): self.inst_progress.pack(fill=tk.X, pady=5); self.inst_progress.start(15); [self.inst_tree.delete(i) for i in self.inst_tree.get_children()]; threading.Thread(target=self.run_installer_scan, args=(p,), daemon=True).start()
    def run_installer_scan(self, path):
        res = []
        for r, d, files in os.walk(path):
            for f in files:
                if f.lower().endswith((".exe", ".msi", ".iso")):
                    fp = os.path.join(r, f)
                    try:
                        if os.path.exists(fp):
                            sz = os.path.getsize(fp)
                            if sz > 1024 * 1024 * 1024: res.append((sz, f, os.path.normpath(r)))
                    except: continue
        self.after(0, self.end_installer_scan, sorted(res, key=lambda x: x, reverse=True))
    def end_installer_scan(self, results):
        for sz, name, f_path in results: self.inst_tree.insert("", tk.END, values=(f"{sz / (1024**3):.2f} GB", name, f_path))
        self.inst_progress.stop(); self.inst_progress.pack_forget()
    def delete_installer_file(self):
        item = self.inst_tree.selection()
        if item:
            try:
                sz, name, folder = self.inst_tree.item(item, "values")
                if messagebox.askyesno("DiskAccuracy", f"Delete {name}?"):
                    os.remove(os.path.join(folder, name))
                    self.inst_tree.delete(item)
            except:
                pass

    def build_fix_tab(self):
        self.btn_u_reg = tk.Button(self.tab_fix, text="", command=self.load_apps)
        self.btn_u_reg.pack(anchor=tk.W, pady=5)
        self.fix_tree = ttk.Treeview(self.tab_fix, columns=("name", "id"), show="headings")
        self.fix_tree.heading("name", text="App Name")
        self.fix_tree.heading("id", text="Registry Key")
        self.fix_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        self.btn_f_reg = tk.Button(self.tab_fix, text="", bg="#ffcccc", command=self.fix_registry)
        self.btn_f_reg.pack(fill=tk.X, pady=5)

    def load_apps(self):
        for i in self.fix_tree.get_children(): self.fix_tree.delete(i)
        for hive, path in [(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"), (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall")]:
            try:
                with winreg.OpenKey(hive, path) as key:
                    for i in range(winreg.QueryInfoKey(key)):
                        try:
                            sub = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, sub) as s_key:
                                name = winreg.QueryValueEx(s_key, "DisplayName")[0]
                                self.fix_tree.insert("", tk.END, values=(name, f"{'HKLM' if hive==winreg.HKEY_LOCAL_MACHINE else 'HKCU'}\\{path}\\{sub}"))
                        except: continue
            except: continue

    def fix_registry(self):
        item = self.fix_tree.selection()
        if item:
            name, full_path = self.fix_tree.item(item, "values")
            if messagebox.askyesno("DiskAccuracy", f"Remove registry entry for {name}?"):
                try:
                    h_str, reg_path = full_path.split("\\", 1)
                    winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE if h_str == "HKLM" else winreg.HKEY_CURRENT_USER, reg_path)
                    self.fix_tree.delete(item)
                except: pass

    def build_hardware_tab(self):
        self.lbl_hw_title = tk.Label(self.tab_hardware, text="", font=("Arial", 11, "bold"))
        self.lbl_hw_title.pack(anchor=tk.W, pady=5)
        self.txt_hw = tk.Text(self.tab_hardware, height=12, font=("Consolas", 10))
        self.txt_hw.pack(fill=tk.X, pady=5)
        try:
            self.txt_hw.insert(tk.END, f"OS: {platform.system()} {platform.release()}\n")
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as k:
                    self.txt_hw.insert(tk.END, f"CPU: {winreg.QueryValueEx(k, 'ProcessorNameString').strip()}\n")
            except:
                self.txt_hw.insert(tk.END, f"CPU: {platform.processor()}\n")
            self.txt_hw.insert(tk.END, f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB RAM\n")
            for part in psutil.disk_partitions():
                if 'fixed' in part.opts:
                    try:
                        u = shutil.disk_usage(part.mountpoint)
                        self.txt_hw.insert(tk.END, f"Drive {part.mountpoint} Total: {u.total/(1024**3):.1f} GB | Free: {u.free/(1024**3):.1f} GB\n")
                    except: pass
        except: pass
        self.txt_hw.config(state=tk.DISABLED)
        self.btn_hw_health = tk.Button(self.tab_hardware, text="", height=2, command=self.check_hw_health)
        self.btn_hw_health.pack(fill=tk.X, pady=10)

    def check_hw_health(self):
        messagebox.showinfo("DiskAccuracy Health Report", "\n".join(["❌ RAM: Высокая нагрузка!" if psutil.virtual_memory().percent > 85 else "🟢 RAM: Память стабильна.", "⚠️ CPU: Перегружен!" if psutil.cpu_percent() > 80 else "🟢 CPU: Нагрузка в норме."]))

    def build_taskmgr_tab(self):
        self.lbl_tm_title = tk.Label(self.tab_taskmgr, text="", font=("Arial", 11, "bold"))
        self.lbl_tm_title.pack(anchor=tk.W, pady=5)
        self.lbl_cpu_live = tk.Label(self.tab_taskmgr, text="CPU Load: 0%", font=("Arial", 14))
        self.lbl_cpu_live.pack(anchor=tk.W, pady=10)
        self.lbl_ram_live = tk.Label(self.tab_taskmgr, text="RAM Load: 0%", font=("Arial", 14))
        self.lbl_ram_live.pack(anchor=tk.W, pady=10)

    def update_task_manager(self):
        try:
            self.lbl_cpu_live.config(text=f"CPU Load: {psutil.cpu_percent()}%")
            self.lbl_ram_live.config(text=f"RAM Load: {psutil.virtual_memory().percent}%")
        except: pass
        self.after(1000, self.update_task_manager)

if __name__ == "__main__":
    DiskAccuracyApp().mainloop()
