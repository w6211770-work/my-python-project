import tkinter as tk
from tkinter import ttk
import re
from pathlib import Path
import os


# ==============================
# Action 基底クラス & 各種 Action
# ==============================

class Action:
    dropdown_name = "不明"

    @classmethod
    def parse(cls, code: str):
        """code から自分の Action を生成できるならインスタンスを返す。できなければ None。"""
        raise NotImplementedError

    def to_code(self) -> str:
        """Python コード文字列として出力"""
        raise NotImplementedError

    def create_widgets(self, parent):
        """
        自分用の入力ウィジェットを parent 上に作成し、
        {名前: Entry/Widget} の dict を返す
        """
        raise NotImplementedError


class WaitAction(Action):
    dropdown_name = "何秒待つ"

    def __init__(self, seconds: int = 1):
        self.seconds = seconds

    @classmethod
    def parse(cls, code: str):
        m = re.match(r"time\.sleep\((\d+)\)", code)
        if m:
            return cls(int(m.group(1)))
        return None

    def to_code(self) -> str:
        return f"time.sleep({self.seconds})"

    def create_widgets(self, parent):
        entry = tk.Entry(parent, width=10)
        entry.insert(0, str(self.seconds))
        entry.pack(side="left")
        return {"seconds": entry}


class ScrollAction(Action):
    dropdown_name = "どれくらいスクロール"

    def __init__(self, amount: int = 100):
        self.amount = amount

    @classmethod
    def parse(cls, code: str):
        m = re.match(r"pyautogui\.scroll\((-?\d+)\)", code)
        if m:
            return cls(int(m.group(1)))
        return None

    def to_code(self) -> str:
        return f"pyautogui.scroll({self.amount})"

    def create_widgets(self, parent):
        entry = tk.Entry(parent, width=10)
        entry.insert(0, str(self.amount))
        entry.pack(side="left")
        return {"amount": entry}


class MoveAction(Action):
    dropdown_name = "どれくらいマウスを移動"

    def __init__(self, x=100, y=100, duration=1):
        self.x = x
        self.y = y
        self.duration = duration

    @classmethod
    def parse(cls, code: str):
        m = re.match(r"pyautogui\.moveTo\((\d+),\s*(\d+)(?:,\s*duration=(\d+))?\)", code)
        if m:
            x = int(m.group(1))
            y = int(m.group(2))
            duration = int(m.group(3)) if m.group(3) else 1
            return cls(x, y, duration)
        return None

    def to_code(self) -> str:
        return f"pyautogui.moveTo({self.x}, {self.y}, duration={self.duration})"

    def create_widgets(self, parent):
        x_entry = tk.Entry(parent, width=6)
        y_entry = tk.Entry(parent, width=6)
        d_entry = tk.Entry(parent, width=6)

        x_entry.insert(0, str(self.x))
        y_entry.insert(0, str(self.y))
        d_entry.insert(0, str(self.duration))

        x_entry.pack(side="left")
        y_entry.pack(side="left")
        d_entry.pack(side="left")

        return {"x": x_entry, "y": y_entry, "duration": d_entry}


class ClickAction(Action):
    dropdown_name = "どこをクリック"

    def __init__(self, x=100, y=100):
        self.x = x
        self.y = y

    @classmethod
    def parse(cls, code: str):
        m = re.match(r"pyautogui\.click\((\d+),\s*(\d+)\)", code)
        if m:
            return cls(int(m.group(1)), int(m.group(2)))
        return None

    def to_code(self) -> str:
        return f"pyautogui.click({self.x}, {self.y})"

    def create_widgets(self, parent):
        x_entry = tk.Entry(parent, width=6)
        y_entry = tk.Entry(parent, width=6)

        x_entry.insert(0, str(self.x))
        y_entry.insert(0, str(self.y))

        x_entry.pack(side="left")
        y_entry.pack(side="left")

        return {"x": x_entry, "y": y_entry}


class WriteAction(Action):
    dropdown_name = "文字入力"

    def __init__(self, text="テキスト"):
        self.text = text

    @classmethod
    def parse(cls, code: str):
        m = re.match(r"pyautogui\.write\(['\"](.+?)['\"]\)", code)
        if m:
            return cls(m.group(1))
        return None

    def to_code(self) -> str:
        return f'pyautogui.write("{self.text}")'

    def create_widgets(self, parent):
        entry = tk.Entry(parent, width=30)
        entry.insert(0, self.text)
        entry.pack(side="left")
        return {"text": entry}


class PressAction(Action):
    dropdown_name = "キー入力"

    # HotkeyAction と同じキー一覧を使う
    KEY_CHOICES = [
        "ctrl", "shift", "alt",
        "cmd", "win",
        "a","b","c","d","e","f","g","h","i","j",
        "k","l","m","n","o","p","q","r","s","t",
        "u","v","w","x","y","z",
        "enter","tab","space","esc","delete","backspace",
        "up","down","left","right"
    ]

    def __init__(self, key="enter"):
        self.key = key

    @classmethod
    def parse(cls, code: str):
        m = re.match(r"pyautogui\.press\(['\"](.+?)['\"]\)", code)
        if m:
            return cls(m.group(1))
        return None

    def to_code(self) -> str:
        return f'pyautogui.press("{self.key}")'

    def create_widgets(self, parent):
        widgets = {}

        cb = ttk.Combobox(parent, values=self.KEY_CHOICES, state="readonly", width=10)
        cb.set(self.key)
        cb.pack(side="left")

        # ★ ActionRow に変更を通知
        cb.bind("<<ComboboxSelected>>", lambda e: parent.event_generate("<<HotkeyChanged>>"))

        widgets["key"] = cb
        return widgets


class HotkeyAction(Action):
    dropdown_name = "ショートカット"

    KEY_CHOICES = [
        "ctrl", "shift", "alt",
        "cmd", "win",
        "a","b","c","d","e","f","g","h","i","j",
        "k","l","m","n","o","p","q","r","s","t",
        "u","v","w","x","y","z",
        "enter","tab","space","esc","delete","backspace",
        "up","down","left","right"
    ]

    def __init__(self, keys=None):
        if keys is None:
            keys = ["ctrl", "c"]
        self.keys = keys

    @classmethod
    def parse(cls, code: str):
        m = re.match(r"pyautogui\.hotkey\((.+)\)", code)
        if m:
            raw = m.group(1)
            keys = [k.strip().strip("'\"") for k in raw.split(",")]
            return cls(keys)
        return None

    def to_code(self) -> str:
        inner = ", ".join(f'"{k}"' for k in self.keys)
        return f"pyautogui.hotkey({inner})"

    def create_widgets(self, parent):
        widgets = {}

        for i, key in enumerate(self.keys):
            cb = ttk.Combobox(parent, values=self.KEY_CHOICES, state="readonly", width=10)
            cb.set(key)
            cb.pack(side="left")

            # ★ 追加：変更時に ActionRow に通知する
            cb.bind("<<ComboboxSelected>>", lambda e: parent.event_generate("<<HotkeyChanged>>"))

            widgets[f"key{i}"] = cb

        return widgets


class DragAction(Action):
    dropdown_name = "ドラッグ"

    def __init__(self, x=200, y=200, duration=1):
        self.x = x
        self.y = y
        self.duration = duration

    @classmethod
    def parse(cls, code: str):
        m = re.match(
            r"pyautogui\.dragTo\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(?:duration\s*=\s*)?([\d\.]+)\s*\)",
            code
        )
        if m:
            x = int(m.group(1))
            y = int(m.group(2))
            duration = float(m.group(3))
            return cls(x, y, duration)
        return None

    def to_code(self) -> str:
        return f"pyautogui.dragTo({self.x}, {self.y}, duration={self.duration})"

    def create_widgets(self, parent):
        x_entry = tk.Entry(parent, width=6)
        y_entry = tk.Entry(parent, width=6)
        d_entry = tk.Entry(parent, width=6)

        x_entry.insert(0, str(self.x))
        y_entry.insert(0, str(self.y))
        d_entry.insert(0, str(self.duration))

        x_entry.pack(side="left")
        y_entry.pack(side="left")
        d_entry.pack(side="left")

        return {"x": x_entry, "y": y_entry, "duration": d_entry}


class CommentAction(Action):
    dropdown_name = "コメント"

    def __init__(self, text="コメント"):
        self.text = text

    @classmethod
    def parse(cls, code: str):
        m = re.match(r"#\s*(.*)", code)
        if m:
            return cls(m.group(1).strip())
        return None

    def to_code(self) -> str:
        return f"# {self.text}"

    def create_widgets(self, parent):
        entry = tk.Entry(parent, width=30)
        entry.insert(0, self.text)
        entry.pack(side="left")
        return {"text": entry}


class LoopAction(Action):
    dropdown_name = "繰り返し"

    def __init__(self, count: int = 5):
        self.count = count

    @classmethod
    def parse(cls, code: str):
        m = re.match(r"for\s+i\s+in\s+range\((\d+)\):?", code)
        if m:
            return cls(int(m.group(1)))
        return None

    def to_code(self) -> str:
        return f"for i in range({self.count}):"

    def create_widgets(self, parent):
        entry = tk.Entry(parent, width=10)
        entry.insert(0, str(self.count))
        entry.pack(side="left")
        return {"count": entry}


class UnknownAction(Action):
    dropdown_name = "不明なコード"

    def __init__(self, raw: str):
        self.raw = raw

    @classmethod
    def parse(cls, code: str):
        # どの Action にもマッチしなかったときに使う
        return None

    def to_code(self) -> str:
        return self.raw

    def create_widgets(self, parent):
        label = tk.Label(parent, text="不明なコード")
        label.pack(side="left")
        return {}


class ImportAction(Action):
    dropdown_name = "import文"

    def __init__(self, code: str):
        self.code = code   # ← import 文全体を保持する

    @classmethod
    def parse(cls, code: str):
        code = code.strip()

        # import xxx
        if code.startswith("import "):
            return cls(code)

        # from xxx import yyy
        if code.startswith("from "):
            return cls(code)

        return None

    def to_code(self) -> str:
        return self.code

    def create_widgets(self, parent):
        # import 文は編集不可 → ラベルだけ
        label = tk.Label(parent, text=self.code, anchor="w")
        label.pack(side="left")
        return {}


# ==============================
# ActionParser
# ==============================

class ActionParser:
    action_classes = [
        ImportAction,
        WaitAction,
        ScrollAction,
        MoveAction,
        ClickAction,
        WriteAction,
        PressAction,
        HotkeyAction,
        DragAction,
        CommentAction,
        LoopAction,
    ]


    @classmethod
    def parse(cls, code: str) -> Action:
        code = code.strip()
        for action_cls in cls.action_classes:
            action = action_cls.parse(code)
            if action is not None:
                return action
        return UnknownAction(code)


# ==============================
# ActionFactory（ドロップダウンから生成）
# ==============================

class ActionFactory:
    name_to_class = {
        a.dropdown_name: a
        for a in ActionParser.action_classes
    }

    @classmethod
    def from_dropdown(cls, name: str) -> Action:
        action_cls = cls.name_to_class.get(name)
        if not action_cls:
            return UnknownAction("# 不明なコード")
        # デフォルトコンストラクタで生成
        return action_cls()


# ==============================
# ActionRow（GUI の1行）
# ==============================

class ActionRow:
    def __init__(self, parent, action: Action, all_dropdown_values, on_changed=None):
        self.parent = parent
        self.action = action
        self.all_dropdown_values = all_dropdown_values
        self.on_changed = on_changed

        self.frame = tk.Frame(parent, highlightthickness=0, bd=0, takefocus=0)
        self.frame.pack(fill="x", anchor="nw", pady=2)

        # ★ import 文だけは特別扱い
        if isinstance(self.action, ImportAction):
            # ラベルだけ表示
            tk.Label(self.frame, text=self.action.to_code(), anchor="w").pack(side="left")
            return  # ← ここで終了（ドロップダウンも＋も－も作らない）

        self.frame.bind("<<HotkeyChanged>>", self._on_entry_changed)

        # ===== 通常の ActionRow =====

        # ラベル（コード表示）
        self.label = tk.Label(self.frame, text=self.action.to_code(), anchor="w")
        self.label.pack(anchor="nw")

        # ドロップダウン
        self.dropdown = ttk.Combobox(self.frame, values=self.all_dropdown_values, state="readonly", width=20)
        self.dropdown.set(self.action.dropdown_name)
        self.dropdown.pack(side="left")
        self.dropdown.bind("<<ComboboxSelected>>", self._on_select)

        # + / - ボタン
        self.add_button = tk.Button(self.frame, text="+", command=self._on_add)
        self.add_button.pack(side="left")

        self.delete_button = tk.Button(self.frame, text="−", command=self._on_delete)
        self.delete_button.pack(side="left")

        # アクション固有ウィジェット
        self.widgets = {}
        self._create_action_widgets()


    def _create_action_widgets(self):
        # 既存ウィジェット削除
        for w in self.widgets.values():
            w.destroy()
        self.widgets.clear()

        # 新規作成
        self.widgets = self.action.create_widgets(self.frame)

        # 値変更時にラベル更新するためのバインド
        for name, widget in self.widgets.items():
            if isinstance(widget, tk.Entry):
                widget.bind("<KeyRelease>", self._on_entry_changed)

        for name, widget in self.widgets.items():
            if isinstance(widget, tk.Entry):
                widget.bind("<KeyRelease>", self._on_entry_changed)
                widget.bind("<FocusIn>", self._on_focus)  # ← これに変更

    def _on_entry_changed(self, event):
        # Entry の値を Action に反映してラベル更新
        self._update_action_from_widgets()
        self.label.config(text=self.action.to_code())
        if self.on_changed:
            self.on_changed()

    def _update_action_from_widgets(self):
        # 各 Action ごとに widget → プロパティ反映
        if isinstance(self.action, WaitAction):
            self.action.seconds = int(self.widgets["seconds"].get() or 0)

        elif isinstance(self.action, ScrollAction):
            self.action.amount = int(self.widgets["amount"].get() or 0)

        elif isinstance(self.action, MoveAction):
            self.action.x = int(self.widgets["x"].get() or 0)
            self.action.y = int(self.widgets["y"].get() or 0)
            self.action.duration = int(self.widgets["duration"].get() or 0)

        elif isinstance(self.action, ClickAction):
            self.action.x = int(self.widgets["x"].get() or 0)
            self.action.y = int(self.widgets["y"].get() or 0)

        elif isinstance(self.action, WriteAction):
            self.action.text = self.widgets["text"].get()

        elif isinstance(self.action, PressAction):
            self.action.key = self.widgets["key"].get()

        elif isinstance(self.action, HotkeyAction):
            new_keys = []
            for name, widget in self.widgets.items():
                if name.startswith("key"):
                    new_keys.append(widget.get())
            self.action.keys = new_keys

        elif isinstance(self.action, DragAction):
            self.action.x = int(self.widgets["x"].get() or 0)
            self.action.y = int(self.widgets["y"].get() or 0)
            self.action.duration = float(self.widgets["duration"].get() or 0)

        elif isinstance(self.action, CommentAction):
            self.action.text = self.widgets["text"].get()

        elif isinstance(self.action, LoopAction):
            self.action.count = int(self.widgets["count"].get() or 0)

    def _on_select(self, event):
        name = self.dropdown.get()
        self.action = ActionFactory.from_dropdown(name)
        self.label.config(text=self.action.to_code())
        self._create_action_widgets()

        # x,y を持つ Action のときだけ focused を更新
        if isinstance(self.action, (MoveAction, ClickAction, DragAction)):
            if self.on_changed:
                self.on_changed(focused=self)

    def _on_add(self):
        if self.on_changed:
            self.on_changed(add_after=self)

    def _on_delete(self):
        self.frame.destroy()
        if self.on_changed:
            self.on_changed(deleted=self)

    def get_code(self) -> str:
        self._update_action_from_widgets()
        return self.action.to_code()

    def _on_focus(self, event):
        if self.on_changed:
            self.on_changed(focused=self)

    def refresh_label(self):
        self.label.config(text=self.action.to_code())


# ==============================

# ==============================
class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("pyautogui DIY OOP版")

        # ============================
        # ここに追加する（最適な位置）
        # ============================
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        screen_height_adjustment = 80

        print(f"screen: {screen_width}x{screen_height}")
        print(f"work area: {screen_width}x{screen_height - screen_height_adjustment}")

        # ウィンドウをタスクバーの上まで表示
        root.geometry(f"{screen_width}x{screen_height - screen_height_adjustment}+0+0")

        # Notebook（タブ）のフォント設定
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Helvetica", 14))

        # ============================
        # Notebook（タブ）
        # ============================
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # --- 新規作成タブ ---
        self.create_tab = CreateTab(self.notebook, self)
        self.notebook.add(self.create_tab.frame, text="新規作成")

        # --- 編集タブ ---
        self.editor_tab = EditorTab(self.notebook)
        self.notebook.add(self.editor_tab.frame, text="編集")

        # --- 実行タブ ---
        self.run_tab = RunTab(self.notebook)
        self.notebook.add(self.run_tab.frame, text="実行")

        # --- 削除タブ ---
        self.delete_tab = DeleteTab(self.notebook)
        self.notebook.add(self.delete_tab.frame, text="削除")
        
        # --- 設定タブ ---
        self.settings_tab = SettingsTab(self.notebook)
        self.notebook.add(self.settings_tab.frame, text="設定")

        self.notebook.select(self.editor_tab.frame)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        tab = event.widget.select()
        selected_frame = event.widget.nametowidget(tab)

        # 編集タブ
        if selected_frame == self.editor_tab.frame:
            self.editor_tab.refresh_file_dropdown()

        # 実行タブ
        elif selected_frame == self.run_tab.frame:
            self.run_tab.refresh_file_dropdown()

        # 削除タブ
        elif selected_frame == self.delete_tab.frame:
            self.delete_tab.refresh_file_dropdown()

    def refresh_editor_file_list(self):
        self.editor_tab.refresh_file_dropdown()


class CreateTab:
    def __init__(self, notebook, main_window):
        self.main_window = main_window
        self.frame = tk.Frame(notebook, highlightthickness=0, bd=0, takefocus=0)

        tk.Label(self.frame, text="新規ファイル名").pack(anchor="w")
        self.entry = tk.Entry(self.frame)
        self.entry.pack(anchor="w")

        tk.Button(self.frame, text="作成", command=self.create_file).pack(anchor="w")

    def create_file(self):
        name = self.entry.get().strip()
        if not name:
            print("ファイル名が空です")
            return

        # ★ python_scripts フォルダに保存する
        folder = Path("python_scripts")
        folder.mkdir(exist_ok=True)

        path = folder / f"{name}.py"

        with open(path, "w", encoding="utf-8") as f:
            f.write("import pyautogui\nimport time\n\n")

        print(f"{path} を作成しました")

        self.main_window.refresh_editor_file_list()


class RunTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, highlightthickness=0, bd=0, takefocus=0)

        tk.Label(self.frame, text="実行するファイル").pack(anchor="w")

        self.dropdown = ttk.Combobox(self.frame, values=self.get_files(), state="readonly")
        self.dropdown.pack(anchor="w")

        tk.Button(self.frame, text="実行", command=self.run_file).pack(anchor="w")

    def get_files(self):
        folder = Path("python_scripts")
        if not folder.exists():
            return []
        return [str(p.name) for p in folder.glob("*.py")]

    def refresh_file_dropdown(self):
        self.dropdown["values"] = self.get_files()

    def run_file(self):
        filename = self.dropdown.get()
        if not filename:
            print("ファイルが選択されていません")
            return

        path = Path(filename)
        if not path.exists():
            print("ファイルが存在しません")
            return

        print(f"{filename} を実行します...")
        os.system(f'python "{filename}"')


class DeleteTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, highlightthickness=0, bd=0, takefocus=0)

        tk.Label(self.frame, text="削除するファイル").pack(anchor="w")

        self.dropdown = ttk.Combobox(self.frame, values=self.get_files())
        self.dropdown.pack(anchor="w")

        tk.Button(self.frame, text="削除", command=self.delete_file).pack(anchor="w")

    def get_files(self):
        folder = Path("python_scripts")
        if not folder.exists():
            return []
        return [str(p.name) for p in folder.glob("*.py")]

    def delete_file(self):
        filename = self.dropdown.get()
        if not filename:
            print("ファイルが選択されていません")
            return

        path = Path("python_scripts") / filename

        if path.exists():
            path.unlink()
            print(f"{filename} を削除しました")

            # ★ ドロップダウンの値を更新
            self.refresh_file_dropdown()

            # ★ 選択状態をクリア
            self.dropdown.set("")

        else:
            print("ファイルが存在しません")

    def refresh_file_dropdown(self):
        self.dropdown["values"] = self.get_files()


class SettingsTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, highlightthickness=0, bd=0, takefocus=0)

        tk.Label(self.frame, text="設定").pack(anchor="w")

        # 例：デフォルト保存フォルダ
        tk.Label(self.frame, text="デフォルト保存フォルダ").pack(anchor="w")
        self.folder_entry = tk.Entry(self.frame, width=40)
        self.folder_entry.insert(0, str(Path.cwd()))
        self.folder_entry.pack(anchor="w")

        tk.Button(self.frame, text="保存", command=self.save_settings).pack(anchor="w")

    def save_settings(self):
        folder = self.folder_entry.get().strip()
        print(f"設定を保存しました: デフォルト保存フォルダ = {folder}")


# ==============================
# Editor
# ==============================

class EditorTab:
    def __init__(self, notebook, filepath: Path | None = None):
        self.frame = tk.Frame(notebook, highlightthickness=0, bd=0, takefocus=0)

        self.filepath = filepath
        self.rows: list[ActionRow] = []

        self.current_row = None

        # -------------------------
        # 上部フレーム
        # -------------------------
        top_frame = tk.Frame(self.frame, highlightthickness=0, bd=0, takefocus=0)
        top_frame.pack(fill="x")

        # ============================================================
        # ★ 追加：python_scripts 内のファイル選択ドロップダウン
        # ============================================================
        tk.Label(top_frame, text="ファイル選択").pack(side="left")

        self.file_dropdown = ttk.Combobox(
            top_frame,
            values=self.get_python_files(),
            state="readonly",
            width=40
        )
        self.file_dropdown.pack(side="left")
        self.file_dropdown.bind("<<ComboboxSelected>>", self.on_file_selected)

        # 保存ボタン
        self.save_button = tk.Button(top_frame, text="保存", command=self.save_file)
        self.save_button.pack(side="left")

        # 行追加ボタン
        self.add_button = tk.Button(top_frame, text="行追加", command=self.add_empty_row)
        self.add_button.pack(side="left")

        # -------------------------
        # スクロールエリア
        # -------------------------
        container = tk.Frame(self.frame, highlightthickness=0, bd=0, takefocus=0)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, highlightthickness=0, bd=0, takefocus=0)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ============================
        # マウスホイールスクロール対応
        # ============================

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Windows / Mac
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Linux（必要なら）
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        # -------------------------
        # ドロップダウン候補
        # -------------------------
        self.dropdown_values = [cls.dropdown_name for cls in ActionParser.action_classes]

        # -------------------------
        # 初期ファイル読み込み
        # -------------------------
        if self.filepath and self.filepath.exists():
            self.load_file(self.filepath)
        else:
            self.add_row(ActionFactory.from_dropdown("何秒待つ"))

        # ============================
        # ★ 編集用の別ウィンドウを開く
        # ============================
        self.edit_window = tk.Toplevel(self.frame)
        self.edit_window.title("x座標, y座標")

        edit_window_width = 300
        edit_window_height = 200

        screen_width = self.frame.winfo_screenwidth()
        screen_height = self.frame.winfo_screenheight()

        edit_window_x = screen_width - edit_window_width - 10
        edit_window_y = 0

        self.edit_window.geometry(
            f"{edit_window_width}x{edit_window_height}+{edit_window_x}+{edit_window_y}"
        )

        # ---------- 四隅フレーム ----------
        corner_frame = tk.Frame(self.edit_window)
        corner_frame.pack(expand=True, fill="both")

        for r in range(3):
            corner_frame.grid_rowconfigure(r, weight=1)
        for c in range(3):
            corner_frame.grid_columnconfigure(c, weight=1)

        # ---------- IntVar ----------
        self.left_top_x = tk.IntVar()
        self.left_top_y = tk.IntVar()
        self.right_top_x = tk.IntVar()
        self.right_top_y = tk.IntVar()
        self.left_bottom_x = tk.IntVar()
        self.left_bottom_y = tk.IntVar()
        self.right_bottom_x = tk.IntVar()
        self.right_bottom_y = tk.IntVar()

        # ---------- ラベル & ボタン（四隅） ----------

        # 左上
        self.label_left_top = tk.Label(corner_frame, text="0, 0", font=14)
        self.label_left_top.grid(row=0, column=0, sticky="nw")

        btn_left_top = tk.Button(
            corner_frame,
            text="転記",
            command=lambda: self.transposing_xy_values(
                self.left_top_x.get(), self.left_top_y.get()
            )
        )
        btn_left_top.grid(row=0, column=0, sticky="sw")

        # 右上
        self.label_right_top = tk.Label(corner_frame, text="0, 0", font=14)
        self.label_right_top.grid(row=0, column=2, sticky="ne")

        btn_right_top = tk.Button(
            corner_frame,
            text="転記",
            command=lambda: self.transposing_xy_values(
                self.right_top_x.get(), self.right_top_y.get()
            )
        )
        btn_right_top.grid(row=0, column=2, sticky="se")

        # 左下
        self.label_left_bottom = tk.Label(corner_frame, text="0, 0", font=14)
        self.label_left_bottom.grid(row=2, column=0, sticky="sw")

        btn_left_bottom = tk.Button(
            corner_frame,
            text="転記",
            command=lambda: self.transposing_xy_values(
                self.left_bottom_x.get(), self.left_bottom_y.get()
            )
        )
        btn_left_bottom.grid(row=2, column=0, sticky="nw")

        # 右下
        self.label_right_bottom = tk.Label(corner_frame, text="0, 0", font=14)
        self.label_right_bottom.grid(row=2, column=2, sticky="se")

        btn_right_bottom = tk.Button(
            corner_frame,
            text="転記",
            command=lambda: self.transposing_xy_values(
                self.right_bottom_x.get(), self.right_bottom_y.get()
            )
        )
        btn_right_bottom.grid(row=2, column=2, sticky="ne")

        # ---------- 座標更新 ----------
        def update_coords():
            x = self.edit_window.winfo_x()
            y = self.edit_window.winfo_y()
            w = self.edit_window.winfo_width()
            h = self.edit_window.winfo_height()

            # 四隅の座標を更新
            self.left_top_x.set(x)
            self.left_top_y.set(y)

            self.right_top_x.set(x + w)
            self.right_top_y.set(y)

            self.left_bottom_x.set(x)
            self.left_bottom_y.set(y + h)

            self.right_bottom_x.set(x + w)
            self.right_bottom_y.set(y + h)

            # ラベルに反映
            self.label_left_top.config(text=f"{x}, {y}")
            self.label_right_top.config(text=f"{x + w}, {y}")
            self.label_left_bottom.config(text=f"{x}, {y + h}")
            self.label_right_bottom.config(text=f"{x + w}, {y + h}")

            self.edit_window.after(100, update_coords)

        update_coords()

        # 最前面に固定
        self.edit_window.attributes("-topmost", True)
        self.edit_window.lift()

        def keep_topmost():
            # 編集タブが選択されている間だけ最前面維持
            current_tab = notebook.select()
            if notebook.nametowidget(current_tab) == self.frame:
                self.edit_window.attributes("-topmost", True)
                self.edit_window.lift()
            else:
                # 編集タブ以外では最前面解除
                self.edit_window.attributes("-topmost", False)

            self.edit_window.after(200, keep_topmost)

        keep_topmost()

        # 閉じるボタンを押したら最小化する
        self.edit_window.protocol("WM_DELETE_WINDOW", self.minimize_edit_window)

    # ============================================================
    # ★ 追加：python_scripts 内の .py ファイル一覧取得
    # ============================================================
    @staticmethod
    def get_python_files():
        folder = Path("python_scripts")
        if not folder.exists():
            return []
        return [str(p.name) for p in folder.glob("*.py")]

    # ============================================================
    # ★ 追加：ファイル選択時の処理
    # ============================================================
    def on_file_selected(self, event):
        filename = self.file_dropdown.get()
        if not filename:
            return

        filepath = Path("python_scripts") / filename
        if not filepath.exists():
            print("ファイルが存在しません")
            return

        # 既存の行をすべて削除
        for row in self.rows:
            row.frame.destroy()
        self.rows.clear()

        # 新しいファイルを読み込む
        self.filepath = filepath
        self.load_file(filepath)

        print(f"{filename} を読み込みました")

    # 以下は既存のメソッド（変更なし）
    def on_row_changed(self, **kwargs):
        # フォーカスされた行
        if "focused" in kwargs:
            self.current_row = kwargs["focused"]
            return

        # 行追加
        if "add_after" in kwargs:
            self.insert_row_after(kwargs["add_after"], ActionFactory.from_dropdown("何秒待つ"))

        # 行削除
        if "deleted" in kwargs:
            self.rows = [r for r in self.rows if r is not kwargs["deleted"]]

    def add_row(self, action: Action):
        row = ActionRow(self.scrollable_frame, action, self.dropdown_values, on_changed=self.on_row_changed)
        self.rows.append(row)

    def insert_row_after(self, target_row: ActionRow, action: Action):
        index = self.rows.index(target_row)
        row = ActionRow(self.scrollable_frame, action, self.dropdown_values, on_changed=self.on_row_changed)
        self.rows.insert(index + 1, row)

    def add_empty_row(self):
        self.add_row(ActionFactory.from_dropdown("何秒待つ"))

    def load_file(self, filepath: Path):
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            code = line.strip()
            if not code:
                continue
            action = ActionParser.parse(code)
            self.add_row(action)

    def save_file(self):
        if not self.filepath:
            self.filepath = Path("output.py")

        with open(self.filepath, "w", encoding="utf-8") as f:
            for row in self.rows:
                f.write(row.get_code() + "\n")

        print(f"保存しました: {self.filepath.resolve()}")

    def refresh_file_dropdown(self):
        self.file_dropdown["values"] = self.get_python_files()

    def minimize_edit_window(self):
        self.edit_window.iconify()

    def transposing_xy_values(self, x, y):
        if not self.current_row:
            print("行が選択されていません")
            return

        action = self.current_row.action

        # --- x, y を持つ Action 共通処理 ---
        if isinstance(action, (MoveAction, ClickAction, DragAction)):
            # 値を Action に反映
            action.x = x
            action.y = y

            # Entry に反映
            self.current_row.widgets["x"].delete(0, tk.END)
            self.current_row.widgets["x"].insert(0, str(x))

            self.current_row.widgets["y"].delete(0, tk.END)
            self.current_row.widgets["y"].insert(0, str(y))

            # ★ ラベル更新（これが重要）
            self.current_row.refresh_label()

            return

        print("この行には x,y を転記できません")


# ==============================
# main
# ==============================
def main():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
