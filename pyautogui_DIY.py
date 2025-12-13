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


def create_file(folder_path, entry):
    filename = entry.get()
    code = ''
    write_file(folder_path=folder_path, filename=filename, code=code)

# =================================================================


# =================================================================
# Pythonファイルの編集
def save_combobox_values(comboboxes, filepath):
    """複数コンボボックスの値を順番に取得してテキストファイルに保存"""
    with open(filepath, "w", encoding="utf-8") as f:
        for combo in comboboxes:
            value = combo
            f.write(value + "\n")
    print(f"save_combobox_values: {filepath} に保存しました")


def select_value(line):
    return_select_value = ''
    if 'moveTo' in line:
        return_select_value = 'どこへマウスを移動'
    elif 'scroll' in line:
        return_select_value = 'どれくらいスクロール'
    elif 'sleep' in line:
        return_select_value = '何秒待つ'
    return return_select_value


def get_dropdown_info(parent, dropdown):
    # タブ内のウィジェットを取得して Combobox だけフィルタリング
    comboboxes = [w for w in parent.winfo_children() if isinstance(w, ttk.Combobox)]
    values = [cb.get() for cb in comboboxes if cb.get() != dropdown]  # 順番通りに値を取得
    print(f'get_dropdown_info 順番通りの値: ', values)
    return values


def save_file(dropdown, dropdowns, folder_path):
    filename = dropdown.get()
    filepath = folder_path / filename
    save_combobox_values(comboboxes=dropdowns, filepath=filepath)
    print(f'save_file: {folder_path}フォルダに{filename}を保存しました')


def edit_selected_file(dropdown, parent, values, folder_path):
    filename = dropdown.get()
    filepath = folder_path / filename
    print(f'edit_selected_fileで編集するファイルパス filepath: {filepath}')
    dropdowns = create_dropdowns_from_textfile(parent=parent, values=values, filepath=filepath, filename=filename)
    frame = create_frame(parent)
    dropdown = create_dropdown(parent=parent, values=values, on_select=on_select, anchor='nw')
    # return dropdowns
# =================================================================


# =================================================================
# Pythonファイルの実行

def run_file(filename):
    subprocess.run(["python", filename])


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

def remove_dropdown(dropdown=None, dropdowns=None):
    # ウィジェットが存在するか確認
    if dropdown and dropdown.winfo_exists():
        dropdown.destroy()

    # まとめて削除
    if dropdowns:
        for d in dropdowns:
            if d.winfo_exists():
                d.destroy()
        dropdowns.clear()


def create_button(parent, button_text, button_command=None):
    button = tkinter.Button(parent, text=button_text, command=button_command)
    apply_pack(widget=button, anchor='nw')


def create_frame(parent):
    frame = tkinter.Frame(parent)
    apply_pack(widget=frame, anchor="nw")

    return frame


def create_entry(parent):
    entry = tkinter.Entry(parent)
    apply_pack(widget=entry, side='left')

    return entry


def create_label(parent, label_text):
    label = tkinter.Label(parent, text=label_text)
    apply_pack(widget=label, anchor="nw",)


def create_tab(notebook, tab_text):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=tab_text)

    return tab


def create_canvas(parent):
    # キャンバスの枠線の表示を消す
    canvas = tkinter.Canvas(parent, highlightthickness=0)
    apply_pack(widget=canvas, side="left", fill="both", expand=True)

    return canvas


def create_container(parent, tab_text):
    container = ttk.Frame(parent)
    parent.add(container, text=tab_text)

    return container


def create_scrollbar(container, canvas):
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    apply_pack(widget=scrollbar, side="right", fill="y")

    return scrollbar


def create_scrollable_tab(notebook, tab_text):
    container = create_container(parent=notebook, tab_text=tab_text)

    canvas = create_canvas(parent=container)

    scrollbar = create_scrollbar(container=container, canvas=canvas)

    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = create_frame(parent=canvas)

    scroll_window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def update_scroll_region(_):
        canvas.configure(scrollregion=canvas.bbox(scroll_window_id))

    scrollable_frame.bind("<Configure>", update_scroll_region)

    # --- マウスホイールイベントをバインド ---
    def _on_mousewheel(event):
        # # Windows / Mac / Linux でイベント値が異なるので調整
        first, last = canvas.yview()
        if event.delta > 0 and first <= 0:  # 上限に到達
            return
        if event.delta < 0 and last >= 1:  # 下限に到達
            return
        canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    # Windows / Mac
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    # Linux (X11)
    canvas.bind_all("<Button-4>", _on_mousewheel)
    canvas.bind_all("<Button-5>", _on_mousewheel)

    return scrollable_frame


def create_file_dropdown(parent, folder_path):
    # フォルダ内のファイル一覧を取得
    files = os.listdir(folder_path)

    dropdown = create_dropdown(parent=parent, values=files, on_select=None, anchor="nw", padx=5, pady=5)

    return dropdown


def create_dropdowns_from_textfile(parent, values, filepath, filename):
    # テキストファイルを読み込み、行ごとのリストを作成
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 各行に対応するプルダウンを作成
    dropdowns = []
    for i, line in enumerate(lines, start=1):
        # ラベル（行の内容を表示）
        text = line.strip()
        create_label(parent=parent, label_text=text)
        # プルダウン（選択肢は共通）
        if line.strip() != filename and 'import' not in line.strip():
            dropdown = create_dropdown(parent=parent, values=values, anchor='nw')
            set_value = select_value(line.strip())
            dropdown.set(set_value)
            dropdowns.append(dropdown)

    return dropdowns


def create_expandable_dropdown(parent, values):
    """ドロップダウンを作成し、選択時に右に新しいドロップダウンを追加"""
    # 1行分の枠を作る
    frame = create_frame(parent=parent)
    apply_pack(widget=frame, fill="x")

    dropdown = create_dropdown(parent=frame, values=values, on_select=on_select, side='left')

    return dropdown


def apply_pack(widget,
               side=None, anchor=None,
               fill=None, expand=None,
               padx=5, pady=5,
               ipadx=None, ipady=None,
               before=None, after=None, in_=None):
    """pack のオプションをまとめて適用するヘルパー関数"""

    pack_options = {
        "side": side,
        "anchor": anchor,
        "fill": fill,
        "expand": expand,
        "padx": padx,
        "pady": pady,
        "ipadx": ipadx,
        "ipady": ipady,
        "before": before,
        "after": after,
        "in_": in_
    }

    widget.pack(**pack_options)


def create_dropdown(parent, values, on_select=None, side=None, anchor=None, padx=None, pady=None):
    combo = ttk.Combobox(parent, values=values, state="readonly")

    apply_pack(combo, side=side, anchor=anchor, padx=padx, pady=pady)

    if on_select:
        combo.bind("<<ComboboxSelected>>", lambda e: on_select(parent=parent, dropdown=combo))
    return combo


def on_select(parent, dropdown):
    selected = dropdown.get()
    print(f"選択された値: {selected}")

    # このコードはIF文で大幅に修正予定。ドロップダウンの内容に応じて、表示する内容を変える。
    # 例えばマウス移動なら、ｘ座標とｙ座標の数字が入力できるエントリーを作る。

    # 右に新しいドロップダウンを追加
    new_values = [f"{selected}_A", f"{selected}_B", f"{selected}_C"]
    create_dropdown(parent=parent, values=new_values, anchor='nw')
    # new_dropdown = ttk.Combobox(parent, values=new_values, state="readonly")
    # new_dropdown.pack(side="left", padx=5)


def create_gui_window(title_name,
                      tab_text_for_create_new,
                      label_text_for_create_new,
                      tab_text_for_edit_file,
                      label_text_for_edit_file,
                      tab_text_for_run_file,
                      label_text_for_run_file,
                      tab_text_for_delete_file,
                      label_text_for_delete_file,
                      tab_text_for_setting,
                      label_text_for_setting,
                      folder_path,
                      choices):
    root = tkinter.Tk()
    root.title(title_name)

    # 画面全体のサイズ
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    screen_height_adjustment = 80
    print(f"screen: {screen_width}x{screen_height}")
    print(f"work area: {screen_width}x{screen_height - screen_height_adjustment}")

    # ウィンドウをタスクバーの上まで表示
    root.geometry(f"{screen_width}x{screen_height - screen_height_adjustment}+0+0")

    # Notebook（タブコンテナ）を作成
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # Notebook（タブコンテナ）の文字を設定
    style = ttk.Style()
    style.configure("TNotebook.Tab", font=("Helvetica", 14))

    # 新規作成タブ
    tab_for_create_new = create_tab(notebook=notebook,
                                    tab_text=tab_text_for_create_new)

    create_label(parent=tab_for_create_new, label_text=label_text_for_create_new)

    frame_for_create_new_tab_decoration = create_frame(parent=tab_for_create_new)

    entry_for_create_new_tab_decoration = create_entry(parent=frame_for_create_new_tab_decoration)

    create_label(parent=frame_for_create_new_tab_decoration, label_text='.py')

    create_button(parent=tab_for_create_new,
                  button_text=tab_text_for_create_new,
                  button_command=lambda: create_file(
                            folder_path=folder_path,
                            entry=entry_for_create_new_tab_decoration))

    # 編集タブ
    tab_for_edit_file = create_scrollable_tab(notebook=notebook,
                                              tab_text=tab_text_for_edit_file)

    frame_for_edit_file_tab_decoration = create_frame(parent=tab_for_edit_file)

    create_label(parent=frame_for_edit_file_tab_decoration, label_text=label_text_for_edit_file)

    dropdown_for_edit_file = create_file_dropdown(parent=frame_for_edit_file_tab_decoration, folder_path=folder_path)

    # 編集ボタンの処理
    create_button(parent=frame_for_edit_file_tab_decoration,
                  button_text=tab_text_for_edit_file,
                  button_command=lambda: edit_selected_file(
                                dropdown=dropdown_for_edit_file,
                                parent=tab_for_edit_file,
                                values=choices,
                                folder_path=folder_path))

    # 保存ボタンの処理
    result_holder = {}

    def on_button_click():
        dropdown = dropdown_for_edit_file.get()
        result_holder["dropdowns"] = get_dropdown_info(parent=frame_for_edit_file_tab_decoration, dropdown=dropdown)
        save_file(dropdown=dropdown_for_edit_file,
                  dropdowns=result_holder["dropdowns"],
                  folder_path=folder_path)

    create_button(parent=frame_for_edit_file_tab_decoration,
                  button_text='保存',
                  button_command=lambda: on_button_click())

    # 実行タブ
    tab_for_run_file = create_tab(notebook=notebook,
                                  tab_text=tab_text_for_run_file)

    create_label(parent=tab_for_run_file, label_text=label_text_for_run_file)

    dropdown_for_run_file = create_file_dropdown(parent=tab_for_run_file, folder_path=folder_path)

    create_button(parent=tab_for_run_file,
                  button_text=tab_text_for_run_file,
                  button_command=lambda: run_selected_file(
                        dropdown=dropdown_for_run_file))

    # 削除タブ
    tab_for_delete_file = create_tab(notebook=notebook,
                                     tab_text=tab_text_for_delete_file)

    create_label(parent=tab_for_delete_file, label_text=label_text_for_delete_file)

    dropdown_for_delete_file = create_file_dropdown(parent=tab_for_delete_file, folder_path=folder_path)

    create_button(parent=tab_for_delete_file,
                  button_text=tab_text_for_delete_file,
                  button_command=lambda: delete_selected_file(
                        dropdown=dropdown_for_delete_file))

    # 設定タブ
    tab_for_setting = create_tab(notebook=notebook,
                                 tab_text=tab_text_for_setting)

    create_label(parent=tab_for_setting, label_text=label_text_for_setting)

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
                  tab_text_for_edit_file='編集',
                  label_text_for_edit_file='編集するファイルを選択してください',
                  tab_text_for_run_file='実行',
                  label_text_for_run_file='実行するファイルを選択してください',
                  tab_text_for_delete_file='削除',
                  label_text_for_delete_file='削除するファイルを選択してください',
                  tab_text_for_setting='設定',
                  label_text_for_setting='設定を行ってください',
                  folder_path=Path('.') / 'python_scripts',
                  choices=['どこへマウスを移動', 'どれくらいスクロール', '何秒待つ'])

●remove_dropdown関数は作成したが、まだ処理に組み込んでいない。
