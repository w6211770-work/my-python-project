# import os
# from core.key_mouse_log import InputMonitor
# from core.key_mouse_log import KeyMouseLogProcessor
# from core.path_resolver import PathResolver


# def main():
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     log_file_path = os.path.join(base_dir, "data", "key_mouse_log.txt")
#
#     monitor = InputMonitor(log_file_path)
#     monitor.start()
#
#     processor = KeyMouseLogProcessor(log_file_path)
#     processor.run(log_file_path)
# def main():
#     log_file_path = PathResolver.KEY_MOUSE_LOG_FILE
#
#     monitor = InputMonitor(log_file_path)
#     monitor.start()
#
#     processor = KeyMouseLogProcessor(log_file_path)
#     processor.run(log_file_path)

import tkinter as tk
from core.pyautogui_DIY import MainWindow


def main():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
