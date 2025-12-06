import pyautogui
import time
import pyperclip
import subprocess
import tkinter
from tkinter import ttk
from pathlib import Path
import os

# このコードはPC作業をノーコードで自動化すること目的としている。
# このコードで下記のことが可能である。
# Pythonファイルの作成
# Pythonファイルの編集
# Pythonファイルの実行
# Pythonファイルの削除


# =================================================================
# 共通処理

# =================================================================


# =================================================================
# Pythonファイルの作成

def write_file(folder_path, filename, code):

    filepath = folder_path / f"{filename}.py"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"{filepath} を作成しました。")


def create_file(folder_path, entry):
    filename = entry.get()
    code = ''
    write_file(folder_path=folder_path, filename=filename, code=code)

# =================================================================


# =================================================================
# Pythonファイルの編集
# def save_combobox_values(comboboxes, filename="いいい.txt"):
#     """複数コンボボックスの値を順番に取得してテキストファイルに保存"""
#     with open(filename, "w", encoding="utf-8") as f:
#         for combo in comboboxes:
#             value = combo.get()
#             f.write(value + "\n")
#     print(f"{filename} に保存しました")


def edit_file(filename):
    print(f'edit_fileで編集するファイル　filename: {filename}')


def edit_selected_file(dropdown, tab, folder_path):
    filename = dropdown.get()
    filepath = folder_path / filename
    print(f'edit_selected_fileで編集するファイルパス filepath: {filepath}')
    create_dropdowns_from_textfile(tab=tab, filepath=filepath)
    edit_file(filename=filename)

# =================================================================


# =================================================================
# Pythonファイルの実行

def run_file(filename):
    subprocess.run(["python", filename])
    print(f"{filename} を実行しました")


def run_selected_file(dropdown):
    filename = dropdown.get()
    run_file(filename=filename)

# =================================================================


# =================================================================
# Pythonファイルの削除
def delete_file(filename):
    delete_filename = Path(filename)

    if delete_filename.exists():
        delete_filename.unlink()
        print(f"{delete_filename} を削除しました")
    else:
        print(f"{delete_filename} は存在しません")


def delete_selected_file(dropdown):
    filename = dropdown.get()
    delete_file(filename=filename)

# =================================================================


# =================================================================
# GUIウィジェットの表示
def create_button(tab, button_text, button_command=None):
    button = tkinter.Button(tab, text=button_text, command=button_command)
    button.pack(padx=10, pady=10)

    return button


def create_entry(tab):
    # 横並び用のフレームを作成
    frame = tkinter.Frame(tab)
    frame.pack(padx=10, pady=10)

    # Entry（入力ボックス）
    entry = tkinter.Entry(frame)
    entry.pack(side=tkinter.LEFT)

    # ラベル（右側に .py を表示）
    label = tkinter.Label(frame, text=".py")
    label.pack(side=tkinter.LEFT)

    return entry


def create_label(tab, label_text):
    label = tkinter.Label(tab, text=label_text)
    label.pack(padx=10, pady=10)


def create_tab(notebook, tab_text):
    """Notebookにタブを追加してラベルを配置する"""
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=tab_text)

    return tab


def create_scrollable_tab(notebook, tab_text):
    container = ttk.Frame(notebook)
    notebook.add(container, text=tab_text)

    canvas = tkinter.Canvas(container, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def update_scroll_region(_):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", update_scroll_region)

    # --- マウスホイールイベントをバインド ---
    def _on_mousewheel(event):
        # Windows / Mac / Linux でイベント値が異なるので調整
        if event.num == 5 or event.delta < 0:    # 下スクロール
            canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:  # 上スクロール
            canvas.yview_scroll(-1, "units")

    # Windows / Mac
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    # Linux (X11)
    canvas.bind_all("<Button-4>", _on_mousewheel)
    canvas.bind_all("<Button-5>", _on_mousewheel)

    return scrollable_frame


def create_file_dropdown(tab, folder_path):
    # フォルダ内のファイル一覧を取得
    files = os.listdir(folder_path)

    # ドロップダウン（プルダウン）
    dropdown = ttk.Combobox(tab, values=files, state="readonly")
    dropdown.pack(padx=10, pady=10)

    # 選択時の処理
    def on_select(_):
        selected_file = dropdown.get()
        print(f"選択されたファイル: {selected_file}")

    dropdown.bind("<<ComboboxSelected>>", on_select)

    return dropdown


def create_dropdowns_from_textfile(tab, filepath):
    # テキストファイルを読み込み、行ごとのリストを作成
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 各行に対応するプルダウンを作成
    dropdowns = []
    for i, line in enumerate(lines, start=1):
        # ラベル（行の内容を表示）
        label = tkinter.Label(tab, text=line.strip())
        label.pack(anchor="w", padx=10, pady=2)

        # プルダウン（選択肢は共通）
        combo = ttk.Combobox(tab, values=["どこをクリック", "どこへマウスを移動"], state="readonly")
        combo.pack(anchor="w", padx=20, pady=2)

        dropdowns.append(combo)

    return dropdowns


def create_gui_window(title_name,
                      tab_text_for_create_new,
                      label_text_for_create_new,
                      tab_text_for_file_editing,
                      label_text_for_file_editing,
                      tab_text_for_run_file,
                      label_text_for_run_file,
                      tab_text_for_delete_file,
                      label_text_for_delete_file,
                      tab_text_for_setting,
                      label_text_for_setting,
                      folder_path):
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

    # 新規作成タブ
    tab_for_create_new = create_tab(notebook=notebook,
                                    tab_text=tab_text_for_create_new)

    create_label(tab=tab_for_create_new, label_text=label_text_for_create_new)

    entry_for_create_new_tab_decoration = create_entry(tab=tab_for_create_new)

    create_button(tab=tab_for_create_new,
                  button_text=tab_text_for_create_new,
                  button_command=lambda: create_file(
                            folder_path=folder_path,
                            entry=entry_for_create_new_tab_decoration))

    # 編集タブ
    tab_for_file_editing = create_scrollable_tab(notebook=notebook,
                                                 tab_text=tab_text_for_file_editing)

    create_label(tab=tab_for_file_editing, label_text=label_text_for_file_editing)

    dropdown_for_edit_file = create_file_dropdown(tab=tab_for_file_editing, folder_path=folder_path)

    create_button(tab=tab_for_file_editing,
                  button_text=tab_text_for_file_editing,
                  button_command=lambda: edit_selected_file(
                        dropdown=dropdown_for_edit_file,
                        tab=tab_for_file_editing,
                        folder_path=folder_path))

    # 実行タブ
    tab_for_run_file = create_tab(notebook=notebook,
                                  tab_text=tab_text_for_run_file)

    create_label(tab=tab_for_run_file, label_text=label_text_for_run_file)

    dropdown_for_run_file = create_file_dropdown(tab=tab_for_run_file, folder_path=folder_path)

    create_button(tab=tab_for_run_file,
                  button_text=tab_text_for_run_file,
                  button_command=lambda: run_selected_file(
                        dropdown=dropdown_for_run_file))

    # 削除タブ
    tab_for_delete_file = create_tab(notebook=notebook,
                                     tab_text=tab_text_for_delete_file)

    create_label(tab=tab_for_delete_file, label_text=label_text_for_delete_file)

    dropdown_for_delete_file = create_file_dropdown(tab=tab_for_delete_file, folder_path=folder_path)

    create_button(tab=tab_for_delete_file,
                  button_text=tab_text_for_delete_file,
                  button_command=lambda: delete_selected_file(
                        dropdown=dropdown_for_delete_file))

    # 設定タブ
    tab_for_setting = create_tab(notebook=notebook,
                                 tab_text=tab_text_for_setting)

    create_label(tab=tab_for_setting, label_text=label_text_for_setting)

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
                  tab_text_for_run_file='実行',
                  label_text_for_run_file='実行するファイルを選択してください',
                  tab_text_for_delete_file='削除',
                  label_text_for_delete_file='削除するファイルを選択してください',
                  tab_text_for_setting='設定',
                  label_text_for_setting='設定を行ってください',
                  folder_path=Path('.') / 'python_scripts')
