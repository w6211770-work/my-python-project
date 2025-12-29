import pyautogui
import time
import pyperclip
import subprocess
import tkinter
from tkinter import ttk
from pathlib import Path
import os
import re

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
def save_label_values(labels, filepath):
    """複数ラベルの値を順番に取得してテキストファイルに保存（空は除外）"""
    with open(filepath, "w", encoding="utf-8") as f:
        for label in labels:
            value = label.cget('text').strip()  # 空白除去
            if value:                           # 空ならスキップ
                f.write(value + "\n")
    print(f"save_label_values: {filepath} に保存しました")


# コードの文字列を順番に引数に設定することで、どんな内容なのか調べて戻り値として返す。
def parse_action(code: str):
    code = code.strip()

    # -------------------------
    # time.sleep(x)
    # -------------------------
    m = re.match(r"time\.sleep\((\d+)\)", code)
    if m:
        sec = m.group(1)
        return {
            "type": "wait",
            "dropdown": "何秒待つ",
            "seconds": sec
        }

    # -------------------------
    # pyautogui.scroll(x)
    # -------------------------
    m = re.match(r"pyautogui\.scroll\((-?\d+)\)", code)
    if m:
        amount = int(m.group(1))
        direction = "下" if amount < 0 else "上"
        return {
            "type": "scroll",
            "dropdown": "どれくらいスクロール",
            "direction": direction,
            "amount": abs(amount)
        }

    # -------------------------
    # pyautogui.moveTo(x, y, duration)
    # -------------------------
    m = re.match(r"pyautogui\.moveTo\((\d+),\s*(\d+)(?:,\s*duration=(\d+))?\)", code)
    if m:
        x = m.group(1)
        y = m.group(2)
        duration = m.group(3)  # duration が無い場合は None

        return {
            "type": "move",
            "dropdown": "どれくらいマウスを移動",
            "x": x,
            "y": y,
            "duration": duration
        }

    # -------------------------
    # pyautogui.click(x, y)
    # -------------------------
    m = re.match(r"pyautogui\.click\((\d+),\s*(\d+)\)", code)
    if m:
        x, y = m.group(1), m.group(2)
        return {
            "type": "click",
            "dropdown": "どこをクリック",
            "x": x,
            "y": y
        }

    # -------------------------
    # pyautogui.write("text")
    # -------------------------
    m = re.match(r"pyautogui\.write\(['\"](.+?)['\"]\)", code)
    if m:
        text = m.group(1)
        return {
            "type": "write",
            "dropdown": "文字入力",
            "text": text
        }

    # -------------------------
    # pyautogui.press("enter")
    # -------------------------
    m = re.match(r"pyautogui\.press\(['\"](.+?)['\"]\)", code)
    if m:
        key = m.group(1)
        return {
            "type": "press",
            "dropdown": "キー入力",
            "key": key
        }

    # -------------------------
    # pyautogui.hotkey("ctrl", "c")
    # -------------------------
    m = re.match(r"pyautogui\.hotkey\((.+)\)", code)
    if m:
        keys = [k.strip().strip("'\"") for k in m.group(1).split(",")]
        return {
            "type": "hotkey",
            "dropdown": "ショートカット",
            "keys": keys
        }

    # -------------------------
    # pyautogui.dragTo(x, y, duration)
    # -------------------------
    m = re.match(r"pyautogui\.dragTo\((\d+),\s*(\d+),\s*([\d\.]+)\)", code)
    if m:
        x, y, duration = m.group(1), m.group(2), m.group(3)
        return {
            "type": "drag",
            "dropdown": "ドラッグ",
            "x": x,
            "y": y,
            "duration": duration
        }

    # -------------------------
    # 不明なコード
    # -------------------------
    return {
        "type": "unknown",
        "dropdown": "不明なコード",
        "raw": code
    }


def save_file(parent, filename_dropdown, folder_path):
    """
    タブ内のすべての Label の値を順番通りに取得して保存する完全版
    """
    # 保存ファイル名
    filename = filename_dropdown.get().strip()
    if not filename:
        print("save_file: ファイル名が空のため保存できません")
        return

    filepath = folder_path / filename

    # タブ内のすべての Label を取得（フレームの中も含む）
    labels = get_all_labels(parent)

    # cord_label のみ取得
    labels = [lb for lb in labels if getattr(lb, "role", None) == "cord_label"]

    # 保存処理（空の値は除外）
    save_label_values(labels=labels, filepath=filepath)

    print(f"save_file: {folder_path} フォルダに {filename} を保存しました")


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

# ドロップダウンの値が変更されたときに、すでに-ボタンより右にウィジェットがある場合、前のドロップダウンの値で作成されたウィジェットであるため削除する
def delete_widgets_right_of_button(frame, exclude_button):
    # -ボタン（削除ボタン）のX座標（frame内での位置）
    ax = exclude_button.winfo_x()

    # frame内のすべての子ウィジェットを調べる
    for widget in frame.winfo_children():
        # -ボタン（削除）自身は削除しない
        if widget is exclude_button:
            continue

        # ウィジェットのX座標
        wx = widget.winfo_x()

        # ボタンAより右にある場合 → 削除
        if wx > ax:
            widget.destroy()


def get_all_labels(widget):
    labels = []
    for child in widget.winfo_children():
        # label なら追加
        if isinstance(child, (tkinter.Label, ttk.Label)):
            labels.append(child)
        # 子供の中も探索（再帰）
        labels.extend(get_all_labels(child))
    return labels


def get_all_dropdowns(widget):
    dropdowns = []
    for child in widget.winfo_children():
        # Combobox なら追加
        if isinstance(child, ttk.Combobox):
            dropdowns.append(child)
        # 子供の中も探索（再帰）
        dropdowns.extend(get_all_dropdowns(child))
    return dropdowns


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


# 編集ボタンが押されたときの処理
# テキストファイルを読み込んでウィジェットを作成する。
def create_dropdowns_from_textfile(parent, values, filepath, filename):
    dropdowns = []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        text = line.strip()

        if text != filename and 'import' not in text:
            # １行ずつパーサー関数で解析
            parsed_text = parse_action(code=text)

            # 新しい行フレーム
            row_frame = tkinter.Frame(parent)
            row_frame.pack(fill='x', anchor='nw')

            # ラベル
            label = tkinter.Label(row_frame, text=text)
            label.pack(anchor='nw')
            label.role = "cord_label"

            # ドロップダウン
            dropdown = ttk.Combobox(row_frame, values=values, state="readonly")
            dropdown.pack(side='left')
            dropdown.set(parsed_text['dropdown'])
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
            delete_button.role = "delete_button"

            # ドロップダウンの選択内容に応じたウィジェット
            apply_parsed_action(result=parsed_text, parent=row_frame, cord_label=label)

    return dropdowns


# 編集ボタンを押して、テキストを読み込んでドロップダウンが表示された後、
# ドロップダウンを変更する操作をしたときのイベントとして、ドロップダウン右に表示されるウィジェットを変更する処理
def on_select(label, dropdown, parent):

    # ドロップダウンの選択された値を取得
    selected = dropdown.get()
    print(f"選択された値: {selected}")

    # ドロップダウンの内容に応じたデフォルトのPythonコードを取得
    default_code = get_default_code_from_dropdown(dropdown_value=selected)

    # デフォルトのPythonコードをラベルに表示
    label.config(text=default_code)

    # -ボタン（削除ボタン）を取得
    exclude_button = None
    for child in parent.winfo_children():
        if isinstance(child, (tkinter.Button, ttk.Button)):
            if getattr(child, "role", None) == "delete_button":
                exclude_button = child
                break

    # -ボタン（削除ボタン）より右にウィジェットがあれば削除する
    delete_widgets_right_of_button(frame=parent, exclude_button=exclude_button)

    # ドロップダウンの内容に応じたウィジェットの作成
    parsed_text = parse_action(default_code)
    apply_parsed_action(result=parsed_text, parent=parent, cord_label=label)


# ドロップダウンの値を使用して、デフォルト値が入った、デフォルトのPythonコードを文字列で返す処理
def get_default_code_from_dropdown(dropdown_value):
    if dropdown_value == "何秒待つ":
        defaults_cord = 'time.sleep(1)'

    elif dropdown_value == "どれくらいスクロール":
        defaults_cord = 'pyautogui.scroll(100)'

    elif dropdown_value == "どれくらいマウスを移動":
        defaults_cord = 'pyautogui.moveTo(100, 100, duration=1)'

    elif dropdown_value == "どこをクリック":
        defaults_cord = 'pyautogui.click(100, 100)'

    elif dropdown_value == "文字入力":
        defaults_cord = 'pyautogui.write("テキスト")'

    elif dropdown_value == "キー入力":
        defaults_cord = 'pyautogui.press("enter")'

    elif dropdown_value == "ショートカット":
        defaults_cord = 'pyautogui.hotkey("ctrl", "c")'

    elif dropdown_value == "ドラッグ":
        defaults_cord = 'pyautogui.dragTo(200, 200, duration=1)'

    else:
        defaults_cord = '# 不明なコード'

    return defaults_cord


# ウィジェットの+ボタンが押されたときの処理
def add_widget_below(current_frame, values):
    # current_frame の親（縦に積んでいる container）
    parent = current_frame.master

    # 新しい行フレームを作る
    new_frame = tkinter.Frame(parent)

    # current_frame の直後に挿入
    new_frame.pack(anchor='nw', after=current_frame)

    # ラベル
    label = tkinter.Label(new_frame)
    label.pack(anchor='nw')
    label.role = "cord_label"

    # ドロップダウン
    combo = ttk.Combobox(new_frame, values=values, state="readonly")
    combo.pack(side='left')
    combo.bind("<<ComboboxSelected>>", lambda e: on_select(label=label, dropdown=combo, parent=new_frame))

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
    delete_button.role = "delete_button"


def delete_row(row_frame):
    if row_frame.winfo_exists():
        row_frame.destroy()


# ドロップダウンの右のウィジェットのエントリーの値が変更されたときにラベルの表示を変える処理
def on_entry_change(_, dropdown_value, label_widget, entries):
    # 全 Entry の値を取得
    values = [entry.get().strip() for entry in entries]

    # 空欄がある場合はラベルをデフォルト値に戻す
    if any(v == "" for v in values):
        default_code = get_default_code_from_dropdown(dropdown_value)
        label_widget.config(text=default_code)
        return

    # ラベルの解析
    parsed_text = parse_action(label_widget.cget("text"))

    # --- 複数 Entry を使うアクション ---
    if parsed_text["dropdown"] == "どれくらいマウスを移動":
        x, y, duration = values
        label_widget.config(text=f'pyautogui.moveTo({x}, {y}, duration={duration})')

    elif parsed_text["dropdown"] == "どこをクリック":
        x, y = values
        label_widget.config(text=f'pyautogui.click({x}, {y})')

    elif parsed_text["dropdown"] == "ドラッグ":
        x, y = values
        label_widget.config(text=f'pyautogui.dragTo({x}, {y}, duration=1)')

    # --- 1つの Entry のアクション ---
    elif parsed_text["dropdown"] == "何秒待つ":
        label_widget.config(text=f'time.sleep({values[0]})')

    elif parsed_text["dropdown"] == "どれくらいスクロール":
        label_widget.config(text=f'pyautogui.scroll({values[0]})')

    elif parsed_text["dropdown"] == "文字入力":
        label_widget.config(text=f'pyautogui.write("{values[0]}")')

    elif parsed_text["dropdown"] == "キー入力":
        label_widget.config(text=f'pyautogui.press("{values[0]}")')

    elif parsed_text["dropdown"] == "ショートカット":
        label_widget.config(text=f'pyautogui.hotkey("{values[0]}")')

    else:
        label_widget.config(text="# 不明なコード")


# def parse_action(code: str)関数で調べたあと、def parse_action(code: str)関数の戻り値を引数に使用してウィジェットを作成する処理
def apply_parsed_action(result, parent, cord_label):
    """
    parse_action の戻り値 result をウィジェットに反映する
    """

    print(result)
    # --- "何秒待つ" ---
    if result["dropdown"] == "何秒待つ":
        entry = tkinter.Entry(parent, width=5)
        entry.pack(side='left')
        entry.delete(0, "end")
        entry.insert(0, str(result["seconds"]))
        entry.bind("<KeyRelease>", lambda e: on_entry_change(e, result["dropdown"], cord_label, [entry]))

        label = tkinter.Label(parent, text='秒待つ')
        label.pack(side='left')

    # --- "どれくらいスクロール" ---
    if result["dropdown"] == "どれくらいスクロール":
        entry = tkinter.Entry(parent, width=7)
        entry.pack(side='left')
        entry.delete(0, "end")
        entry.insert(0, str(result["amount"]))
        entry.bind("<KeyRelease>", lambda e: on_entry_change(e, result["dropdown"], cord_label, [entry]))

        label = tkinter.Label(parent, text='スクロール(例：－200＝下に200スクロール、300＝上に300スクロール)')
        label.pack(side='left')

    # --- "どれくらいマウスを移動" ---
    if result["dropdown"] == "どれくらいマウスを移動":
        label_x = tkinter.Label(parent, text='x:')
        label_x.pack(side='left')

        entry_x = tkinter.Entry(parent, width=4)
        entry_x.pack(side='left')
        entry_x.delete(0, "end")
        entry_x.insert(0, str(result["x"]))
        entry_x.bind("<KeyRelease>", lambda e: on_entry_change(e,
                                                               result["dropdown"],
                                                               cord_label,
                                                               [entry_x, entry_y, entry_duration]))

        label = tkinter.Label(parent, text='  ')
        label.pack(side='left')

        label_y = tkinter.Label(parent, text='y:')
        label_y.pack(side='left')

        entry_y = tkinter.Entry(parent, width=4)
        entry_y.pack(side='left')
        entry_y.delete(0, "end")
        entry_y.insert(0, str(result["y"]))
        entry_y.bind("<KeyRelease>", lambda e: on_entry_change(e,
                                                               result["dropdown"],
                                                               cord_label,
                                                               [entry_x, entry_y, entry_duration]))

        label = tkinter.Label(parent, text=' の位置に ')
        label.pack(side='left')

        entry_duration = tkinter.Entry(parent, width=4)
        entry_duration.pack(side='left')
        entry_duration.delete(0, "end")
        entry_duration.insert(0, str(result["duration"]))
        entry_duration.bind("<KeyRelease>", lambda e: on_entry_change(e,
                                                                      result["dropdown"],
                                                                      cord_label,
                                                                      [entry_x, entry_y, entry_duration]))

        label_duration = tkinter.Label(parent, text='秒かけて移動')
        label_duration.pack(side='left')

        label = tkinter.Label(parent,
                              text=('にマウス移動(例：x:200、y:600 、duration:3'
                                    '　＝ 画面左上から右に200ピクセル,下に600ピクセルの位置に3秒かけてマウス移動)'))
        label.pack(side='left')


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

    # フォルダ内のファイル一覧を取得
    files = os.listdir(folder_path)
    dropdown_for_edit_file = ttk.Combobox(frame_for_edit_file_tab_decoration,
                                          values=files,
                                          state="readonly")
    dropdown_for_edit_file.pack(anchor='nw')
    dropdown_for_edit_file.bind("<<ComboboxSelected>>",
                                lambda event: edit_selected_file(dropdown=dropdown_for_edit_file,
                                                                 parent=tab_for_edit_file,
                                                                 values=choices,
                                                                 folder_path=folder_path))

    # dropdown_for_edit_file.set('test2.py')

    # 保存ボタンの処理
    def on_button_click():
        save_file(parent=tab_for_edit_file,
                  filename_dropdown=dropdown_for_edit_file,
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

    # フォルダ内のファイル一覧を取得
    files = os.listdir(folder_path)
    dropdown_for_run_file = ttk.Combobox(tab_for_run_file, values=files, state="readonly")
    dropdown_for_run_file.pack(anchor='nw')

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

    # フォルダ内のファイル一覧を取得
    files = os.listdir(folder_path)
    dropdown_for_delete_file = ttk.Combobox(tab_for_delete_file, values=files, state="readonly")
    dropdown_for_delete_file.pack(anchor='nw')

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
                  choices=['何秒待つ', 'どれくらいスクロール', 'どれくらいマウスを移動', "どこをクリック", "文字入力", "キー入力", "ショートカット", "ドラッグ"])
