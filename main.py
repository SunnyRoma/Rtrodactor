import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# Попробуем использовать пиксельный шрифт, если он есть
PIXEL_FONT = ("Consolas", 12, "bold")

class RetroEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ретродактор")
        self.geometry("900x600")
        
        # Устанавливаем иконку приложения
        try:
            self.iconbitmap('retro_editor.ico')
        except:
            pass  # Если иконка не найдена, используем стандартную
            
        self.configure(bg="#fff")
        self.tabs = []
        self.theme = 'light'
        self.recent_files = []
        self.autosave_interval = 30000  # 30 секунд
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        recent_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.recent_menu = recent_menu
        self.menu_bar.add_cascade(label='Недавние', menu=recent_menu)
        self.create_widgets()
        self.update_recent_menu()
        self.after(self.autosave_interval, self.autosave)

    def create_widgets(self):
        # Верхняя рамка
        self.top_frame = tk.Frame(self, bg="#fff", highlightbackground="#000", highlightthickness=3)
        self.top_frame.pack(fill=tk.X, padx=20, pady=(20, 0))
        self.logo = tk.Label(self.top_frame, text="📝  Ретродактор v1.0", font=("Consolas", 16, "bold"), bg="#fff")
        self.logo.pack(side=tk.LEFT, padx=10, pady=5)

        # Кнопки
        self.button_frame = tk.Frame(self, bg="#fff", highlightbackground="#000", highlightthickness=3)
        self.button_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        self.new_btn = self.retro_button(self.button_frame, "Новый", self.new_file, "#4fc3f7")
        self.open_btn = self.retro_button(self.button_frame, "Открыть", self.open_file, "#81c784")
        self.save_btn = self.retro_button(self.button_frame, "Сохранить", self.save_file, "#ffd54f")
        self.export_btn = self.retro_button(self.button_frame, "Экспорт", self.show_export_menu, "#81c784")
        self.settings_btn = self.retro_button(self.button_frame, "⚙️", self.toggle_settings, "#ffd54f")
        self.new_btn.pack(side=tk.LEFT, padx=10, pady=10)
        self.open_btn.pack(side=tk.LEFT, padx=10, pady=10)
        self.save_btn.pack(side=tk.LEFT, padx=10, pady=10)
        self.export_btn.pack(side=tk.LEFT, padx=10, pady=10)
        self.settings_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # Основной контейнер
        self.main_container = tk.Frame(self, bg="#fff")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 0))

        # Рамка для вкладок
        self.text_frame = tk.Frame(self.main_container, bg="#fff", highlightbackground="#000", highlightthickness=3)
        self.text_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.notebook = ttk.Notebook(self.text_frame)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.close_tab_btn = tk.Button(self.text_frame, text='✖', font=("Consolas", 14, "bold"), bg="#ffd54f", fg="#111", bd=2, relief=tk.FLAT, command=self.close_current_tab)
        self.close_tab_btn.pack(side=tk.LEFT, padx=(5,0), pady=10, anchor='n')

        # Панель настроек (изначально скрыта)
        self.settings_frame = tk.Frame(self.main_container, bg="#fff", highlightbackground="#000", highlightthickness=3, width=300)
        self.settings_frame.pack(fill=tk.BOTH, side=tk.RIGHT, padx=(10, 0))
        self.settings_frame.pack_forget()  # Скрываем панель настроек

        # Содержимое панели настроек
        settings_content = tk.Frame(self.settings_frame, bg="#fff")
        settings_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Тема
        tk.Label(settings_content, text='Тема:', font=("Consolas", 12, "bold")).pack(anchor='w', pady=(10,2))
        self.theme_var = tk.StringVar(value=self.theme)
        frame_theme = tk.Frame(settings_content)
        frame_theme.pack(anchor='w')
        tk.Radiobutton(frame_theme, text='Светлая', variable=self.theme_var, value='light', font=("Consolas", 11), command=self.apply_settings).pack(side=tk.LEFT)
        tk.Radiobutton(frame_theme, text='Тёмная', variable=self.theme_var, value='dark', font=("Consolas", 11), command=self.apply_settings).pack(side=tk.LEFT)

        # Шрифт
        tk.Label(settings_content, text='Шрифт:', font=("Consolas", 12, "bold")).pack(anchor='w', pady=(10,2))
        self.font_family_var = tk.StringVar(value=PIXEL_FONT[0])
        self.font_size_var = tk.IntVar(value=PIXEL_FONT[1])
        frame_font = tk.Frame(settings_content)
        frame_font.pack(anchor='w')
        tk.Label(frame_font, text='Семейство:', font=("Consolas", 11)).pack(side=tk.LEFT)
        font_families = ['Consolas', 'Courier New', 'Arial']
        font_family_menu = ttk.Combobox(frame_font, textvariable=self.font_family_var, values=font_families, width=12)
        font_family_menu.pack(side=tk.LEFT, padx=5)
        font_family_menu.bind('<<ComboboxSelected>>', lambda e: self.apply_settings())
        
        tk.Label(frame_font, text='Размер:', font=("Consolas", 11)).pack(side=tk.LEFT, padx=(10,0))
        font_size_menu = ttk.Combobox(frame_font, textvariable=self.font_size_var, values=[10, 12, 14, 16, 18, 20], width=4)
        font_size_menu.pack(side=tk.LEFT, padx=5)
        font_size_menu.bind('<<ComboboxSelected>>', lambda e: self.apply_settings())

        # Надпись внизу
        tk.Label(settings_content, text='Сделано с ❤️ Pygrammer', font=("Consolas", 11), fg="#888").pack(side=tk.BOTTOM, pady=5)

        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', font=PIXEL_FONT, padding=[10, 5], background="#e0e0e0", foreground="#111")
        style.map('TNotebook.Tab', background=[('selected', '#fff176')])

        # Нижняя рамка
        self.bottom_frame = tk.Frame(self, bg="#fff", highlightbackground="#000", highlightthickness=3)
        self.bottom_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        self.status = tk.Label(self.bottom_frame, text="Ретродактор", font=("Consolas", 10), bg="#fff")
        self.status.pack(side=tk.LEFT, padx=10, pady=5)

        # Вкладка по умолчанию
        self.add_tab()

        self.bind_all('<Control-n>', lambda e: self.new_file())
        self.bind_all('<Control-o>', lambda e: self.open_file())
        self.bind_all('<Control-s>', lambda e: self.save_file())
        self.bind_all('<Control-w>', lambda e: self.close_current_tab())
        self.bind_all('<Control-f>', lambda e: self.open_find_dialog())
        self.bind_all('<Control-h>', lambda e: self.open_replace_dialog())

        self.notebook.bind('<ButtonPress-1>', self.on_tab_drag_start)
        self.notebook.bind('<B1-Motion>', self.on_tab_drag_motion)
        self.notebook.bind('<ButtonRelease-1>', self.on_tab_drag_end)

        self._drag_data = {'tab': None, 'x': 0}

    def toggle_settings(self):
        if self.settings_frame.winfo_ismapped():
            self.settings_frame.pack_forget()
        else:
            self.settings_frame.pack(fill=tk.BOTH, side=tk.RIGHT, padx=(10, 0))

    def apply_settings(self):
        self.set_theme(self.theme_var.get())
        self.set_font(self.font_family_var.get(), self.font_size_var.get())

    def retro_button(self, parent, text, command, color):
        btn = tk.Button(parent, text=text, font=PIXEL_FONT, bg=color, fg="#111", activebackground="#fff176", activeforeground="#111", bd=3, relief=tk.FLAT, command=command)
        btn.configure(highlightbackground="#000", highlightthickness=2)
        return btn

    def add_tab(self, content="", filename=None):
        frame = tk.Frame(self.notebook, bg="#fff")
        text = tk.Text(frame, font=PIXEL_FONT, bg="#f9f9f9", fg="#111", insertbackground="#111", bd=0, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, content)
        tab_title = os.path.basename(filename) if filename else "Без имени"
        self.notebook.add(frame, text=tab_title)
        self.tabs.append({'text': text, 'filename': filename, 'modified': False})
        self.notebook.select(len(self.tabs)-1)
        text.bind("<<Modified>>", lambda e, idx=len(self.tabs)-1: self.on_tab_modified(idx))
        text.bind("<KeyRelease>", lambda e: self.update_status())  # Обновляем при каждом нажатии клавиши
        text.bind("<ButtonRelease>", lambda e: self.update_status())  # Обновляем при выделении текста мышью
        self.update_status()

    def on_tab_modified(self, idx):
        tab = self.tabs[idx]
        text_widget = tab['text']
        if text_widget.edit_modified():
            tab['modified'] = True
            title = os.path.basename(tab['filename']) if tab['filename'] else "Без имени"
            self.notebook.tab(idx, text="*" + title)
            text_widget.edit_modified(False)
        else:
            tab['modified'] = False
            title = os.path.basename(tab['filename']) if tab['filename'] else "Без имени"
            self.notebook.tab(idx, text=title)

    def get_current_tab(self):
        idx = self.notebook.index(self.notebook.select())
        return self.tabs[idx], idx

    def new_file(self):
        tab, idx = self.get_current_tab()
        if tab['text'].get("1.0", tk.END).strip():
            if not messagebox.askyesno("Новый файл", "Открыть новую вкладку? Несохранённые данные будут потеряны."):
                return
        self.add_tab()

    def open_file(self):
        files = filedialog.askopenfilenames(defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
        for file in files:
            if file:
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.add_tab(content, file) 
                    self.add_to_recent(file)
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def save_file(self):
        tab, idx = self.get_current_tab()
        filename = tab['filename']
        if not filename:
            file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")])
            if not file:
                return
            filename = file
            self.tabs[idx]['filename'] = filename
            self.notebook.tab(idx, text=os.path.basename(filename))
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(tab['text'].get("1.0", tk.END))
            self.status.config(text=f"Сохранено: {os.path.basename(filename)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
        self.update_status()

    def update_status(self):
        tab, idx = self.get_current_tab()
        name = os.path.basename(tab['filename']) if tab['filename'] else "Без имени"
        content = tab['text'].get("1.0", tk.END)
        lines = content.count('\n') + 1  # +1 потому что последняя строка может не иметь \n
        chars = len(content.rstrip('\n'))  # Убираем последний \n из подсчета символов
        self.status.config(text=f"Вкладка: {name} | Строк: {lines} | Символов: {chars}")

    def close_current_tab(self):
        tab, idx = self.get_current_tab()
        if tab['modified']:
            if not messagebox.askyesno("Закрыть вкладку", "Есть несохранённые изменения. Всё равно закрыть?"):
                return
        self.notebook.forget(idx)
        self.tabs.pop(idx)
        if not self.tabs:
            self.add_tab()
        self.update_status()

    def open_find_dialog(self):
        tab, idx = self.get_current_tab()
        text_widget = tab['text']
        def do_find():
            text_widget.tag_remove('found', '1.0', tk.END)
            find_text = entry.get()
            if not find_text:
                return
            start = '1.0'
            while True:
                pos = text_widget.search(find_text, start, stopindex=tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(find_text)}c"
                text_widget.tag_add('found', pos, end)
                start = end
            text_widget.tag_config('found', background='#fff176', foreground='#111')
        win = tk.Toplevel(self)
        win.title('Поиск')
        win.geometry('300x80')
        tk.Label(win, text='Найти:').pack(pady=5)
        entry = tk.Entry(win)
        entry.pack(fill=tk.X, padx=10)
        entry.focus_set()
        tk.Button(win, text='Найти', command=do_find).pack(pady=5)

    def open_replace_dialog(self):
        tab, idx = self.get_current_tab()
        text_widget = tab['text']
        def do_replace():
            find_text = entry_find.get()
            replace_text = entry_replace.get()
            content = text_widget.get('1.0', tk.END)
            new_content = content.replace(find_text, replace_text)
            text_widget.delete('1.0', tk.END)
            text_widget.insert('1.0', new_content)
        win = tk.Toplevel(self)
        win.title('Замена')
        win.geometry('300x120')
        tk.Label(win, text='Найти:').pack(pady=2)
        entry_find = tk.Entry(win)
        entry_find.pack(fill=tk.X, padx=10)
        tk.Label(win, text='Заменить на:').pack(pady=2)
        entry_replace = tk.Entry(win)
        entry_replace.pack(fill=tk.X, padx=10)
        tk.Button(win, text='Заменить всё', command=do_replace).pack(pady=5)

    def set_theme(self, theme):
        self.theme = theme
        if theme == 'dark':
            bg = '#222'
            fg = '#eee'
            tab_bg = '#444'
            tab_fg = '#fff'
            text_bg = '#222'
            text_fg = '#eee'
        else:
            bg = '#fff'
            fg = '#111'
            tab_bg = '#e0e0e0'
            tab_fg = '#111'
            text_bg = '#f9f9f9'
            text_fg = '#111'
        self.configure(bg=bg)
        self.top_frame.configure(bg=bg)
        self.button_frame.configure(bg=bg)
        self.text_frame.configure(bg=bg)
        self.bottom_frame.configure(bg=bg)
        self.status.configure(bg=bg, fg=fg)
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', font=PIXEL_FONT, padding=[10, 5], background=tab_bg, foreground=tab_fg)
        style.map('TNotebook.Tab', background=[('selected', '#fff176' if theme=='light' else '#666')])
        for tab in self.tabs:
            tab['text'].configure(bg=text_bg, fg=text_fg, insertbackground=fg)

    def set_font(self, family, size):
        global PIXEL_FONT
        PIXEL_FONT = (family, size, "bold")
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=PIXEL_FONT)
        for tab in self.tabs:
            tab['text'].configure(font=PIXEL_FONT)
        self.logo.configure(font=(family, 16, "bold"))
        self.status.configure(font=(family, 10))

    def on_tab_drag_start(self, event):
        self._drag_data['tab'] = self.notebook.index(f"@{event.x},{event.y}")
        self._drag_data['x'] = event.x

    def on_tab_drag_motion(self, event):
        idx = self._drag_data['tab']
        if idx is None:
            return
        new_idx = self.notebook.index(f"@{event.x},{event.y}")
        if new_idx != idx and new_idx >= 0:
            self.tabs.insert(new_idx, self.tabs.pop(idx))
            self.notebook.insert(new_idx, self.notebook.tabs()[idx])
            self._drag_data['tab'] = new_idx

    def on_tab_drag_end(self, event):
        self._drag_data['tab'] = None
        self._drag_data['x'] = 0

    def add_to_recent(self, file):
        if file in self.recent_files:
            self.recent_files.remove(file)
        self.recent_files.insert(0, file)
        self.recent_files = self.recent_files[:10]
        self.update_recent_menu()

    def update_recent_menu(self):
        self.recent_menu.delete(0, tk.END)
        for file in self.recent_files:
            self.recent_menu.add_command(label=file, command=lambda f=file: self.open_recent(f))

    def open_recent(self, file):
        if os.path.isfile(file):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                self.add_tab(content, file)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def show_export_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Экспорт в HTML", command=self.export_html)
        if HAS_FPDF:
            menu.add_command(label="Экспорт в PDF", command=self.export_pdf)
        # Показываем меню под кнопкой экспорта
        x = self.export_btn.winfo_rootx()
        y = self.export_btn.winfo_rooty() + self.export_btn.winfo_height()
        menu.post(x, y)

    def export_html(self):
        tab, idx = self.get_current_tab()
        file = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML файлы", "*.html")])
        if not file:
            return
        content = tab['text'].get("1.0", tk.END)
        html = f"<html><body><pre>{content}</pre></body></html>"
        with open(file, "w", encoding="utf-8") as f:
            f.write(html)
        messagebox.showinfo("Экспорт", "Экспортировано в HTML!")

    def export_pdf(self):
        if not HAS_FPDF:
            messagebox.showerror("Ошибка", "Модуль fpdf не установлен!")
            return
        tab, idx = self.get_current_tab()
        file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF файлы", "*.pdf")])
        if not file:
            return
        content = tab['text'].get("1.0", tk.END)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in content.splitlines():
            pdf.cell(0, 10, line, ln=1)
        pdf.output(file)
        messagebox.showinfo("Экспорт", "Экспортировано в PDF!")

    def autosave(self):
        for tab in self.tabs:
            if tab['filename'] and tab['modified']:
                try:
                    with open(tab['filename'], "w", encoding="utf-8") as f:
                        f.write(tab['text'].get("1.0", tk.END))
                    tab['modified'] = False
                except Exception:
                    pass
        self.after(self.autosave_interval, self.autosave)

if __name__ == "__main__":
    app = RetroEditor()
    # Если передан путь к файлу — открыть его во вкладке
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # Удаляем вкладку по умолчанию, если она пустая и без имени
                tab, idx = app.get_current_tab()
                if not tab['filename'] and not tab['text'].get("1.0", tk.END).strip():
                    app.notebook.forget(idx)
                    app.tabs.pop(idx)
                app.add_tab(content, file_path)
            except Exception as e:
                app.status.config(text=f"Ошибка открытия: {e}")
    app.mainloop()
