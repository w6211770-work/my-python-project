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
    # parent=tab_for_edit_file
    filename = dropdown.get()
    filepath = folder_path / filename
    print(f'edit_selected_fileで編集するファイルパス filepath: {filepath}')

    # 前のファイルのドロップダウン等が表示されていればフレームごとドロップダウン等を消去
    exclude_frame = dropdown.master
    remove_frame(parent=parent, exclude_frame=exclude_frame)

    # 編集するファイルを読み込みドロップダウンを作成
    create_dropdowns_from_textfile(parent=parent, values=values, filepath=filepath, filename=filename)
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
def get_all_frames(widget):
    frames = []
    for child in widget.winfo_children():
        # Frame なら追加
        if isinstance(child, tkinter.Frame):
            frames.append(child)
        # 子供の中も探索（再帰）
        frames.extend(get_all_frames(child))
    return frames


def remove_frame(parent, exclude_frame=None):
    frames = get_all_frames(parent)

    if exclude_frame:
        # 除外対象以外を削除
        for f in frames:
            if f.winfo_exists() and f is not exclude_frame:
                f.destroy()
    else:
        # 全部削除
        for f in frames:
            if f.winfo_exists():
                f.destroy()

# def get_dropdowns_in_tab(parent):
#     dropdowns = [child for child in parent.winfo_children() if isinstance(child, (tkinter.OptionMenu, ttk.Combobox))]
#
#     return dropdowns
# def get_all_dropdowns(widget):
#     dropdowns = []
#     for child in widget.winfo_children():
#         # Combobox なら追加
#         if isinstance(child, ttk.Combobox):
#             dropdowns.append(child)
#         # 子供の中も探索（再帰）
#         dropdowns.extend(get_all_dropdowns(child))
#     return dropdowns
#
#
# def get_labels_in_tab(parent):
#     labels = [child for child in parent.winfo_children() if isinstance(child, (tkinter.Label, ttk.Label))]
#
#     return labels
#
#
# def remove_dropdown(parent, exclude_dropdown=None):
#     dropdowns = get_all_dropdowns(parent)
#
#     if exclude_dropdown:
#         # 除外対象以外を削除
#         for d in dropdowns:
#             if d.winfo_exists() and d is not exclude_dropdown:
#                 d.destroy()
#         # exclude を残すためにリストを再構築
#         dropdowns[:] = [d for d in dropdowns if d is exclude_dropdown]
#     else:
#         # 全部削除
#         for d in dropdowns:
#             if d.winfo_exists():
#                 d.destroy()
#         dropdowns.clear()
#
#
# def remove_label(parent, exclude_label=None):
#     labels = get_labels_in_tab(parent)
#
#     if exclude_label:
#         # 除外対象以外を削除
#         for d in labels:
#             if d.winfo_exists() and d is not exclude_label:
#                 d.destroy()
#         # exclude を残すためにリストを再構築
#         labels[:] = [d for d in labels if d is exclude_label]
#     else:
#         # 全部削除
#         for d in labels:
#             if d.winfo_exists():
#                 d.destroy()
#         labels.clear()


def create_scrollable_tab(notebook, tab_text):
    # コンテナ作成
    container = ttk.Frame(notebook)
    notebook.add(container, text=tab_text)
    notebook.select(container)

    # キャンバス作成
    canvas = tkinter.Canvas(container, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    # スクロールバー作成
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = tkinter.Frame(canvas)

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

    dropdown = ttk.Combobox(parent, values=files, state="readonly")
    dropdown.pack(anchor='nw')

    return dropdown


def create_dropdowns_from_textfile(parent, values, filepath, filename):
    dropdowns = []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        text = line.strip()

        if text != filename and 'import' not in text:
            # 新しい行フレーム
            row_frame = tkinter.Frame(parent)
            row_frame.pack(fill='x', anchor='nw')

            # ラベル
            label = tkinter.Label(row_frame, text=text)
            label.pack(anchor='nw')

            # ドロップダウン
            dropdown = ttk.Combobox(row_frame, values=values, state="readonly")
            dropdown.pack(side='left')
            dropdown.set(select_value(text))
            dropdowns.append(dropdown)

            # +ボタン（行追加）
            add_button = tkinter.Button(
                row_frame,
                text="+",
                command=lambda fr=row_frame: add_widget_below(fr, values)
            )
            add_button.pack(side='left')

            # -ボタン（行削除）
            delete_button = tkinter.Button(
                row_frame,
                text="−",
                command=lambda fr=row_frame: delete_row(fr)
            )
            delete_button.pack(side='left')

    return dropdowns


def on_select(parent, dropdown):
    selected = dropdown.get()
    print(f"選択された値: {selected}")
    # このコードはIF文で大幅に修正予定。ドロップダウンの内容に応じて、表示する内容を変える。
    # 例えばマウス移動なら、ｘ座標とｙ座標の数字が入力できるエントリーを作る。

    # 右に新しいドロップダウンを追加
    new_values = [f"{selected}_A", f"{selected}_B", f"{selected}_C"]
    dropdown = ttk.Combobox(parent, values=new_values, state="readonly")
    dropdown.pack(side='left')


def add_widget_below(current_frame, values):
    # current_frame の親（縦に積んでいる container）
    parent = current_frame.master

    # 新しい行フレームを作る
    new_frame = tkinter.Frame(parent)

    # ★ current_frame の直後に挿入
    new_frame.pack(after=current_frame)

    # 新しいドロップダウンを作る
    combo = ttk.Combobox(new_frame, values=values, state="readonly")
    combo.pack(side='left')
    combo.bind("<<ComboboxSelected>>", lambda e: on_select(parent=new_frame, dropdown=combo))

    # +ボタン（行追加）
    add_button = tkinter.Button(
        new_frame,
        text="+",
        command=lambda f=new_frame: add_widget_below(f, values)
    )
    add_button.pack(side='left')

    # -ボタン（行削除）
    delete_button = tkinter.Button(
        new_frame,
        text="−",
        command=lambda f=new_frame: delete_row(f)
    )
    delete_button.pack(side='left')


def delete_row(row_frame):
    if row_frame.winfo_exists():
        row_frame.destroy()


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
    tab_for_create_new = ttk.Frame(notebook)
    notebook.add(tab_for_create_new, text=tab_text_for_create_new)

    label_for_create_new = tkinter.Label(tab_for_create_new, text=label_text_for_create_new)
    label_for_create_new.pack()

    frame_for_create_new_tab_decoration = tkinter.Frame(tab_for_create_new)
    frame_for_create_new_tab_decoration.pack()

    entry_for_create_new_tab_decoration = tkinter.Entry(frame_for_create_new_tab_decoration)
    entry_for_create_new_tab_decoration.pack()

    label_for_create_new_tab_decoration = tkinter.Label(frame_for_create_new_tab_decoration, text='.py')
    label_for_create_new_tab_decoration.pack()

    button_for_create_new_tab_decoration = tkinter.Button(frame_for_create_new_tab_decoration,
                                                          text=tab_text_for_create_new,
                                                          command=lambda: create_file(
                                                            folder_path=folder_path,
                                                            entry=entry_for_create_new_tab_decoration))
    button_for_create_new_tab_decoration.pack()

    # 編集タブ
    tab_for_edit_file = create_scrollable_tab(notebook=notebook, tab_text=tab_text_for_edit_file)

    frame_for_edit_file_tab_decoration = tkinter.Frame(tab_for_edit_file)
    frame_for_edit_file_tab_decoration.pack(anchor='nw')

    label_for_edit_file_tab_decoration = tkinter.Label(frame_for_edit_file_tab_decoration,
                                                       text=label_text_for_edit_file)
    label_for_edit_file_tab_decoration.pack()

    dropdown_for_edit_file = create_file_dropdown(parent=frame_for_edit_file_tab_decoration, folder_path=folder_path)
    dropdown_for_edit_file.set('test2.py')

    # 編集ボタンの処理
    button_for_edit_file_tab_decoration = tkinter.Button(frame_for_edit_file_tab_decoration,
                                                         text=tab_text_for_edit_file,
                                                         command=lambda: edit_selected_file(
                                                            dropdown=dropdown_for_edit_file,
                                                            parent=tab_for_edit_file,
                                                            values=choices,
                                                            folder_path=folder_path))
    button_for_edit_file_tab_decoration.pack()

    # 保存ボタンの処理
    result_holder = {}

    def on_button_click():
        dropdown = dropdown_for_edit_file.get()
        result_holder["dropdowns"] = get_dropdown_info(parent=frame_for_edit_file_tab_decoration, dropdown=dropdown)
        save_file(dropdown=dropdown_for_edit_file,
                  dropdowns=result_holder["dropdowns"],
                  folder_path=folder_path)

    save_button_for_edit_file_tab_decoration = tkinter.Button(frame_for_edit_file_tab_decoration,
                                                              text='保存',
                                                              command=lambda: on_button_click())
    save_button_for_edit_file_tab_decoration.pack()

    # 実行タブ
    tab_for_run_file = ttk.Frame(notebook)
    notebook.add(tab_for_run_file, text=tab_text_for_run_file)

    label_for_run_file = tkinter.Label(tab_for_run_file, text=label_text_for_run_file)
    label_for_run_file.pack()

    dropdown_for_run_file = create_file_dropdown(parent=tab_for_run_file, folder_path=folder_path)

    button_for_run_file = tkinter.Button(tab_for_run_file,
                                         text=tab_text_for_run_file,
                                         command=lambda: run_selected_file(
                                            dropdown=dropdown_for_run_file))
    button_for_run_file.pack()

    # 削除タブ
    tab_for_delete_file = ttk.Frame(notebook)
    notebook.add(tab_for_delete_file, text=tab_text_for_delete_file)

    label_for_delete_file = tkinter.Label(tab_for_delete_file, text=label_text_for_delete_file)
    label_for_delete_file.pack()

    dropdown_for_delete_file = create_file_dropdown(parent=tab_for_delete_file, folder_path=folder_path)

    button_for_delete_file = tkinter.Button(tab_for_delete_file,
                                            text=tab_text_for_delete_file,
                                            command=lambda: delete_selected_file(
                                                dropdown=dropdown_for_delete_file))
    button_for_delete_file.pack()

    # 設定タブ
    tab_for_setting = ttk.Frame(notebook)
    notebook.add(tab_for_setting, text=tab_text_for_setting)

    label_for_setting = tkinter.Label(tab_for_setting, text=label_text_for_setting)
    label_for_setting.pack()

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
