import pyautogui
import time
time.sleep(1)
pyautogui.click(524, 292, button='left')
pyautogui.dragTo(524, 296, button='left')
pyautogui.hotkey('ctrl', 'a')
pyautogui.hotkey('ctrl', 'c')
pyautogui.click(37, 144, button='left')