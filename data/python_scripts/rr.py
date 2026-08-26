import pyautogui
import time
time.sleep(1)
pyautogui.click(374, 207, button='left')
pyautogui.dragTo(374, 207, button='left')
pyautogui.click(803, 473, button='left')
pyautogui.hotkey('ctrl', 'a')
pyautogui.hotkey('ctrl', 'c')
pyautogui.click(35, 143, button='left')