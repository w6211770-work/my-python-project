import time
import pyautogui
pyautogui.moveTo(1153, 1040, duration=2)
pyautogui.click(1153, 1040)
pyautogui.write("hello")
pyautogui.click(1153, 830)
time.sleep(2)
pyautogui.press("enter")
