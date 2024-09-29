import tkinter as tk
import tarfile
import time
import xml.etree.ElementTree as ET
import argparse
import socket

# Класс виртуальной файловой системы
class VirtualFileSystem:
    def __init__(self, tar_path):
        self.root = {}
        self.current_dir = self.root
        self.path_stack = []

        self.load_tar(tar_path)

    def load_tar(self, tar_path):
    # Загрузка содержимого архива tar
        with tarfile.open(tar_path, 'r') as tar:
            for member in tar.getmembers():
                parts = [part for part in member.name.split('/') if part]
                d = self.root
                for part in parts:
                    if part not in d:
                        d[part] = {}
                    d = d[part]

    def ls(self):
        return list(self.current_dir.keys())

    def cd(self, dir_name):
        if dir_name == '..':
            if self.path_stack:
                self.path_stack.pop()
                self.current_dir = self.root
                for dir in self.path_stack:
                    self.current_dir = self.current_dir[dir]
        elif dir_name in self.current_dir:
            self.path_stack.append(dir_name)
            self.current_dir = self.current_dir[dir_name]
        else:
            raise FileNotFoundError(f"No such directory: {dir_name}")

    def pwd(self):
        return '/' + '/'.join(self.path_stack) if self.path_stack else '/'

    def tree(self, dir=None, indent=""):
        if dir is None:
            dir = self.current_dir
        result = ""
        for key, value in dir.items():
            result += indent + key + "\n"
            if isinstance(value, dict):
                result += self.tree(value, indent + "  ")
        return result

# Логирование действий пользователя в XML
class Logger:
    def __init__(self, log_file, user):
        self.log_file = log_file
        self.user = user
        self.root = ET.Element("log")

    def log(self, command):
        entry = ET.Element("entry")
        user_element = ET.SubElement(entry, "user")
        user_element.text = self.user
        time_element = ET.SubElement(entry, "time")
        time_element.text = time.strftime("%Y-%m-%d %H:%M:%S")
        command_element = ET.SubElement(entry, "command")
        command_element.text = command
        self.root.append(entry)

    def save(self):
        tree = ET.ElementTree(self.root)
        tree.write(self.log_file)

# Функция для обновления приглашения
def update_prompt():
    current_path = vfs.pwd()
    prompt = f"{args.user}@{hostname}:{current_path}$ "
    output_text.config(state=tk.NORMAL)
    output_text.insert(tk.END, prompt)
    output_text.config(state=tk.DISABLED)
    output_text.yview_moveto(1.0)

# Функция для обработки команд
def execute(event=None):
    input_text = input_entry.get()  # Получаем текст из поля ввода
    command = input_text.strip().split()  # Разделяем команду и аргументы

    output_text.config(state=tk.NORMAL)
    try:
        if command[0] == 'ls':
            result = '\n'.join(vfs.ls())
        elif command[0] == 'cd':
            if len(command) > 1:
                vfs.cd(command[1])
                result = ""
            else:
                result = "Directory not specified"
        elif command[0] == 'pwd':
            result = vfs.pwd()
        elif command[0] == 'tree':
            result = vfs.tree()
        elif command[0] == 'exit':
            logger.save()
            root.quit()
            return
        else:
            result = "Unknown command"
    except Exception as e:
        result = str(e)

    # Добавляем результат в текстовое поле вывода
    output_text.insert(tk.END, f"{input_text}\n{result}\n")
    output_text.config(state=tk.DISABLED)
    output_text.yview_moveto(1.0)
    input_entry.delete(0, tk.END)
    logger.log(input_text)
    update_prompt()


if __name__ == "__main__":
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description="Эмулятор командной строки")
    parser.add_argument('--user', required=True, help="Имя пользователя для показа в приглашении к вводу")
    parser.add_argument('--tar', required=True, help="Путь к архиву виртуальной файловой системы (tar)")
    parser.add_argument('--log', required=True, help="Путь к лог-файлу (xml)")
    args = parser.parse_args()

    # Получаем имя хоста
    hostname = socket.gethostname()

    # Создаем виртуальную файловую систему и логгер с использованием аргументов
    vfs = VirtualFileSystem(args.tar)
    logger = Logger(args.log, args.user)

    # Создаем главное окно
    root = tk.Tk()
    root.title(f"Командная строка - Пользователь: {args.user}")
    root.geometry("600x400")
    root.configure(bg="black")

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(0, weight=1)

    # Поле для вывода (используем Text и делаем его не редактируемым)
    output_frame = tk.Frame(root, bg="black")
    output_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    output_text = tk.Text(output_frame, font=("Courier", 12), bg="black", fg="white", highlightbackground="white", highlightthickness=2, wrap="word")
    output_text.pack(fill="both", expand=True, padx=5, pady=5)
    output_text.config(state=tk.DISABLED)

    # Добавляем прокрутку
    scrollbar = tk.Scrollbar(output_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    output_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=output_text.yview)

    # Рамка для поля ввода и кнопки
    input_frame = tk.Frame(root, bg="black")
    input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    # Поле для ввода текста (моноширинный шрифт, белая рамка)
    input_entry = tk.Entry(input_frame, font=("Courier", 12), highlightbackground="white", highlightthickness=1, bg="black", fg="white", insertbackground="white")
    input_entry.pack(side="left", fill="x", expand=True)

    # Кнопка "Execute"
    execute_button = tk.Button(input_frame, text="Execute", command=execute, font=("Courier", 12), highlightbackground="white", highlightthickness=2, bg="black", fg="white")
    execute_button.pack(side="right", padx=5)

    # Привязываем клавишу Enter к функции execute
    root.bind('<Return>', execute)

    # Функция для приветственного сообщения
    def display_welcome_message():
        welcome_message = f"Hello, {args.user}!\n"
        output_text.config(state=tk.NORMAL)
        output_text.insert(tk.END, welcome_message)
        output_text.config(state=tk.DISABLED)
        output_text.yview_moveto(1.0)

    # Выводим приветственное сообщение
    display_welcome_message()

    # Изначально выводим приглашение
    update_prompt()

    # Запуск основного цикла приложения
    root.mainloop()
