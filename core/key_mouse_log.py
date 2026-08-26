from pynput import keyboard
from pynput import mouse
import time
import re
import os


VK_TO_CHAR = {
    65: "a",
    66: "b",
    67: "c",
    68: "d",
    69: "e",
    70: "f",
    71: "g",
    72: "h",
    73: "i",
    74: "j",
    75: "k",
    76: "l",
    77: "m",
    78: "n",
    79: "o",
    80: "p",
    81: "q",
    82: "r",
    83: "s",
    84: "t",
    85: "u",
    86: "v",
    87: "w",
    88: "x",
    89: "y",
    90: "z",
}

VK_TO_PYAUTO = {
    162: "ctrl",   # ctrl_l
    163: "ctrl",   # ctrl_r
    160: "shift",  # shift_l
    161: "shift",  # shift_r
    164: "alt",    # alt_l
    165: "alt",    # alt_r
}


# ============================
# 共通ロガー
# ============================
class Logger:
    def __init__(self, log_file="key_mouse_log.txt"):
        self.log_file = log_file

    def write(self, text):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(text + "\n")
        print(text)


# ============================
# マウス検知クラス
# ============================
class MouseDetector:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.is_pressed = False
        self.is_dragging = False
        self.start_pos = None

    def extract_button_name(self, button):
        return str(button).split('.')[-1]

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.is_pressed = True
            self.start_pos = (x, y)
            self.logger.write(f"pyautogui.click({x}, {y}, button='{self.extract_button_name(button)}')")
            # self.logger.write(f"クリック: {button} at ({x}, {y})")

        else:
            if self.is_dragging:
                self.logger.write(f"pyautogui.dragTo({x}, {y}, button='{self.extract_button_name(button)}')")
                # self.logger.write(f"ドラッグ終了: {button} at ({x}, {y})")

            # 状態リセット
            self.is_pressed = False
            self.is_dragging = False
            self.start_pos = None

    def on_move(self, x, y):
        if self.is_pressed:
            if not self.is_dragging:
                self.is_dragging = True

    def on_scroll(self, x, y, dx, dy):
        self.logger.write(f"pyautogui.scroll({dy*100})")
        # self.logger.write(f"スクロール: ({dx}, {dy}) at ({x}, {y})")


# ============================
# キーボード検知クラス
# ============================
class KeyboardDetector:
    def __init__(self, logger, hotkeys=None):
        self.logger = logger
        self.pressed_keys = set()
        self.key_states = {}  # 押下状態を管理（True=押されている）
        self.hotkeys = hotkeys or {}

    def normalize_key(self, key):
        # 特殊キー
        if isinstance(key, keyboard.Key):
            return str(key).replace("Key.", "")

        # 通常キー
        elif isinstance(key, keyboard.KeyCode):
            vk = key.vk
            if vk in VK_TO_CHAR:
                return VK_TO_CHAR[vk]  # 65 → "a"
            return None

        return None

    def on_press(self, key):
        char = self.normalize_key(key)
        vk = key.vk if hasattr(key, "vk") else key.value

        if self.key_states.get(vk, False):
            return

        self.key_states[vk] = True

        if char:
            self.logger.write(f"pyautogui.keyDown('{char}')")
        else:
            self.logger.write(f"# 特殊キー VK={vk}")

    def on_release(self, key):
        char = self.normalize_key(key)
        vk = key.vk if hasattr(key, "vk") else key.value

        if vk is None:
            return

        # 押下状態を解除
        self.key_states[vk] = False

        # pyautogui 出力
        if char:
            self.logger.write(f"pyautogui.keyUp('{char}')")
        else:
            self.logger.write(f"# 特殊キー VK={vk} 離す")

        # ESCで終了
        if key == keyboard.Key.esc:
            self.logger.write("ESCで終了")
            return False


# ============================
# 監視システム（責務分離）
# ============================
class InputMonitor:
    def __init__(self, log_file="key_mouse_log.txt"):
        self.logger = Logger(log_file)
        # ホットキー登録（VKコードで統一）
        hotkeys = {
            frozenset([
                keyboard.Key.ctrl_l.value,  # 162
                65  # keyboard.KeyCode.from_char('a').vk  # 65
            ]): lambda: print("Ctrl + A 発動"),

            frozenset([
                keyboard.Key.ctrl_l.value,          # 162
                83  # keyboard.KeyCode.from_char('s').vk  # 83
            ]): lambda: print("Ctrl + S 発動"),

            frozenset([
                keyboard.Key.ctrl_l.value,          # 162
                keyboard.Key.shift.value,           # 16
                68  # keyboard.KeyCode.from_char('d').vk  # 68
            ]): lambda: print("Ctrl + Shift + D 発動")
        }

        self.mouse_detector = MouseDetector(self.logger)
        self.keyboard_detector = KeyboardDetector(self.logger, hotkeys)

        self.mouse_listener = mouse.Listener(
            on_click=self.mouse_detector.on_click,
            on_move=self.mouse_detector.on_move,
            on_scroll=self.mouse_detector.on_scroll
        )

        self.keyboard_listener = keyboard.Listener(
            on_press=self.keyboard_detector.on_press,
            on_release=self.keyboard_detector.on_release
        )

    def start(self):
        print("=== 入力監視開始 ===")

        # ここでファイルを上書き（空にする）
        with open(self.logger.log_file, "w", encoding="utf-8") as f:
            f.write("")

        self.logger.write(f"import pyautogui")
        self.logger.write(f"import time")
        self.logger.write(f"pyautogui.PAUSE = 0.3")
        self.logger.write(f"time.sleep(1)")
        self.mouse_listener.start()
        self.keyboard_listener.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        print("=== 入力監視終了 ===")
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
    # def stop(self):
    #     print("=== 入力監視終了 ===")
    #
    #     try:
    #         self.mouse_listener.stop()
    #     except:
    #         pass
    #
    #     try:
    #         self.keyboard_listener.stop()
    #     except:
    #         pass
    #
    #     # Listener を確実に停止させるためのダミーイベント
    #     try:
    #         from pynput.keyboard import Controller
    #         kb = Controller()
    #         kb.press(' ')
    #         kb.release(' ')
    #     except:
    #         pass
    #
    #     # ★ 最終手段：Listener スレッドを強制終了
    #     try:
    #         self.mouse_listener._thread.join(timeout=0.5)
    #     except:
    #         pass
    #
    #     try:
    #         self.keyboard_listener._thread.join(timeout=0.5)
    #     except:
    #         pass


class KeyMouseLogProcessor:
    CTRL_KEYS = ["ctrl", "ctrl_l", "ctrl_r"]

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lines = []
        self.output = []
        self.ctrl_pressed = False
        self.pressed_keys = []

    # ===== 判定系メソッド =====
    def is_ctrl_down(self, line: str) -> bool:
        return any(
            f"pyautogui.keyDown('{ck}')" in line or
            f"pyautogui.keyDown(\"{ck}\")" in line
            for ck in self.CTRL_KEYS
        )

    def is_ctrl_up(self, line: str) -> bool:
        return any(
            f"pyautogui.keyUp('{ck}')" in line or
            f"pyautogui.keyUp(\"{ck}\")" in line
            for ck in self.CTRL_KEYS
        )

    def extract_key_from_line(self, line: str, kind: str) -> str | None:
        # kind: "keyDown" or "keyUp"
        m = re.findall(rf"{kind}\(['\"](.+?)['\"]\)", line)
        return m[0] if m else None

    # ===== メイン処理 =====
    def load(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.lines = f.readlines()

    def process(self):
        self.output = []
        self.ctrl_pressed = False
        self.pressed_keys = []

        for line in self.lines:
            stripped = line.strip()

            # Ctrl押下開始
            if self.is_ctrl_down(stripped):
                self.ctrl_pressed = True
                self.pressed_keys = []
                continue

            # Ctrl離す（最優先で判定）
            if self.ctrl_pressed and self.is_ctrl_up(stripped):
                self.ctrl_pressed = False

                for key in self.pressed_keys:
                    self.output.append(f"pyautogui.hotkey('ctrl', '{key}')")

                continue

            # Ctrl押下中のキー押下
            if self.ctrl_pressed and "pyautogui.keyDown(" in stripped:
                key = self.extract_key_from_line(stripped, "keyDown")
                if key and key not in self.CTRL_KEYS:
                    self.pressed_keys.append(key)
                continue

            # Ctrl押下中のキー離し（Ctrl系以外）
            if self.ctrl_pressed and "pyautogui.keyUp(" in stripped:
                key = self.extract_key_from_line(stripped, "keyUp")
                if key and key not in self.CTRL_KEYS:
                    # Ctrl中の非CtrlキーUpは無視
                    continue
                continue

            # 通常行
            self.output.append(stripped)

    # def save(self):
    #     with open(self.file_path, "w", encoding="utf-8") as f:
    #         f.write("\n".join(self.output))
    def save(self, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.output))

    # def run(self):
    #     self.load()
    #     self.process()
    #     self.save()
    #     print("修正完了：Ctrl離し判定を最優先にして、誤判定を完全に防ぎました。")
    def run(self, output_path: str):
        self.load()
        self.process()
        self.save(output_path)
        print("変換完了：.py ファイルを生成しました")

# ============================
# 実行
# ============================
#
# if __name__ == "__main__":
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     log_file_path = os.path.join(base_dir, "data", "key_mouse_log.txt")
#     key_mouse_log_file_name = log_file_path
#     monitor = InputMonitor(key_mouse_log_file_name)
#     monitor.start()
#
#     processor = KeyMouseLogProcessor(key_mouse_log_file_name)
#     processor.run()
if __name__ == "__main__":
    # ★ core の 1 つ上のフォルダ（プロジェクトルート）を取得
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ★ data/key_mouse_log.txt を絶対パスで指定
    log_file_path = os.path.join(project_root, "data", "key_mouse_log.txt")

    # ★ InputMonitor と Processor に絶対パスを渡す
    monitor = InputMonitor(log_file_path)
    monitor.start()

    processor = KeyMouseLogProcessor(log_file_path)
    processor.run(log_file_path)