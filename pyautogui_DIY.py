import pyautogui
import time
import pyperclip
import subprocess
import tkinter
from tkinter import ttk

# このコードはPC作業をノーコードで自動化すること目的としている。
# このコードで下記のことが可能である。
# Pythonファイルの作成
# Pythonファイルの編集
# Pythonファイルの実行


# =================================================================
# Pythonファイルの作成

def write_file(filename, code):
    # 新しいPythonファイルを作成して内容を書き込むコード
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"{filename} を作成しました。")

# =================================================================


# =================================================================
# Pythonファイルの編集


# =================================================================


# =================================================================
# Pythonファイルの実行

def run_python_file(filename):
    # Pythonでファイルを実行
    subprocess.run(["python", filename])

# =================================================================


# =================================================================
# GUIウィジェットの表示

def create_tab(notebook, tab_text, label_text, button_text=None, button_command=None):
    """Notebookにタブを追加してラベルとボタンを配置する"""
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=tab_text)

    label = tkinter.Label(tab, text=label_text)
    label.pack(padx=10, pady=10)

    if button_text:
        button = tkinter.Button(tab, text=button_text, command=button_command)
        button.pack(padx=10, pady=10)

    return tab

def create_gui_window(title_name,
                      tab_text_for_create_new,
                      label_text_for_create_new,
                      tab_text_for_file_editing,
                      label_text_for_file_editing,
                      tab_text_for_run_python_file,
                      label_text_for_run_python_file,
                      tab_text_for_setting,
                      label_text_setting):
    root = tkinter.Tk()
    root.title(title_name)

    # 画面いっぱいに画面サイズを設定
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")

    # Notebook（タブコンテナ）を作成
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # Notebook（タブコンテナ）の文字を設定
    style = ttk.Style()
    style.configure("TNotebook.Tab", font=("Helvetica", 14))

    # ボタンを押したら入力値を取得
    def show_value():
        value = entry.get()
        print("入力された値:", value)

    # 左タブを作成
    tab_for_create_new = ttk.Frame(notebook)
    notebook.add(tab_for_create_new, text=tab_text_for_create_new)
    label_for_create_new = tkinter.Label(tab_for_create_new, text=label_text_for_create_new)
    label_for_create_new.pack(padx=10, pady=10)

    # 左タブ専用ボタン
    button_create = tkinter.Button(tab_for_create_new, text=tab_text_for_create_new, command=show_value)
    button_create.pack(padx=10, pady=10)

    # Entry（入力ボックス）
    entry = tkinter.Entry(tab_for_create_new)
    entry.pack(padx=10, pady=10)

    # 中央タブを作成
    tab_for_file_editing = ttk.Frame(notebook)
    notebook.add(tab_for_file_editing, text=tab_text_for_file_editing)
    label_for_file_editing = tkinter.Label(tab_for_file_editing, text=label_text_for_file_editing)
    label_for_file_editing.pack(padx=10, pady=10)

    # 中央タブ専用ボタン
    button_edit = tkinter.Button(tab_for_file_editing, text=tab_text_for_file_editing)
    button_edit.pack(padx=10, pady=10)

    # 右タブを作成
    tab_for_run_python_file = ttk.Frame(notebook)
    notebook.add(tab_for_run_python_file, text=tab_text_for_run_python_file)
    label_for_run_python_file = tkinter.Label(tab_for_run_python_file, text=label_text_for_run_python_file)
    label_for_run_python_file.pack(padx=10, pady=10)

    # 右タブ専用ボタン
    button_run = tkinter.Button(tab_for_run_python_file, text=tab_text_for_run_python_file)
    button_run.pack(padx=10, pady=10)

    # 設定タブを作成
    tab_for_setting = ttk.Frame(notebook)
    notebook.add(tab_for_setting, text=tab_text_for_setting)
    label_for_setting = tkinter.Label(tab_for_setting, text=label_text_setting)
    label_for_setting.pack(padx=10, pady=10)

    # 設定タブ専用ボタン
    button_setting = tkinter.Button(tab_for_setting, text=tab_text_for_setting)
    button_setting.pack(padx=10, pady=10)

    root.mainloop()

# =================================================================
# code = """import pyautogui
# pyautogui.moveTo(1500, 1000)
# """
#
# # ファイル名を指定
# filename = "PY_GUI.py"


create_gui_window(title_name='pyautogui_DIY',
                  tab_text_for_create_new='新規作成',
                  label_text_for_create_new='新規作成するファイル名を入力してください',
                  tab_text_for_file_editing='編集',
                  label_text_for_file_editing='編集するファイルを選択してください',
                  tab_text_for_run_python_file='実行',
                  label_text_for_run_python_file='実行するファイルを選択してください',
                  tab_text_for_setting='設定',
                  label_text_setting='設定を行ってください')

