# New Recoil Suspension with Listener
import time
from pynput import mouse
from pynput.mouse import Controller
from pynput import keyboard
import win32api
import win32con
import PySimpleGUI as sg

CTRL_Mouse = Controller()

WeaponMode = "FullAuto"
k_RC_1 = 5
k_RC_2 = 5
k_RC_value = 5

IsStateChange = True

IsLeftKeyPressing = False
IsSuspensionActive = False
IsMapOpen = False
IsInventoryOpen = False
IsUIOpen = False
IsGMOpen = False
timer_ForcedAuto = 0


def recoil_compensate():
    global IsLeftKeyPressing, IsSuspensionActive, WeaponMode
    global k_RC_1, k_RC_2
    global timer_ForcedAuto
    if IsLeftKeyPressing and IsSuspensionActive:
        if not IsUIOpen:
            if WeaponMode == "FullAuto":
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, k_RC_1, 0, 0)

            elif WeaponMode == "ForcedAuto":
                timer_ForcedAuto = 0
                timer_ForcedAuto = timer_ForcedAuto + 1
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, k_RC_2, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)


def on_click(x, y, button, pressed):
    global IsLeftKeyPressing, IsSuspensionActive, WeaponMode, IsStateChange
    global timer_ForcedAuto
    if pressed and button == mouse.Button.left:
        IsLeftKeyPressing = True
    elif pressed and button == mouse.Button.x2:
        IsStateChange = True
        if IsSuspensionActive:
            IsSuspensionActive = False
        else:
            IsSuspensionActive = True
        print("Suspension State:", IsSuspensionActive)
    elif pressed and button == mouse.Button.x1:
        IsStateChange = True
        if WeaponMode == "FullAuto":
            WeaponMode = "ForcedAuto"
        elif WeaponMode == "ForcedAuto":
            WeaponMode = "FullAuto"
        print("Weapon Mode:", WeaponMode)

    else:
        IsLeftKeyPressing = False


def on_press(key):
    global IsGMOpen
    try:
        if key.char == 'g':
            IsGMOpen = True
        elif key.char == '`':
            IsGMOpen = True
        else:
            IsGMOpen = False
    except AttributeError:
        pass


def on_release(key):
    global IsMapOpen, IsInventoryOpen, IsUIOpen, IsStateChange, IsGMOpen
    global k_RC_1, k_RC_2

    try:
        if key.char == 'm':
            IsStateChange = True
            if not IsMapOpen:
                IsMapOpen = True
            else:
                IsMapOpen = False

            if IsInventoryOpen:
                IsInventoryOpen = False

        elif key.char == 'g':
            IsGMOpen = False

        elif key.char == '`':
            IsGMOpen = False

    except AttributeError:

        if key == keyboard.Key.esc:
            IsStateChange = True
            IsMapOpen = False
            IsInventoryOpen = False

        elif key == keyboard.Key.tab:
            IsStateChange = True
            if not IsInventoryOpen:
                IsInventoryOpen = True
            else:
                IsInventoryOpen = False
            if IsMapOpen:
                IsMapOpen = False

        elif key == keyboard.Key.up:
            if IsSuspensionActive:
                if WeaponMode == "FullAuto":
                    k_RC_1 = k_RC_1 + 1
                elif WeaponMode == "ForcedAuto":
                    k_RC_2 = k_RC_2 + 1
                IsStateChange = True

        elif key == keyboard.Key.down:
            if IsSuspensionActive:
                if WeaponMode == "FullAuto":
                    k_RC_1 = k_RC_1 - 1
                elif WeaponMode == "ForcedAuto":
                    k_RC_2 = k_RC_2 - 1
                IsStateChange = True

        print("k_RC_1", k_RC_1)
        print("k_RC_2", k_RC_2)

    IsUIOpen = IsMapOpen or IsInventoryOpen


def define_window():
    global layout_1, window_1
    layout_1 = [[
        sg.Text("Active:"+str(IsSuspensionActive), key='P1', background_color="white", text_color="red"),
        sg.Text("UI Open:"+str(IsUIOpen), key='P2', background_color="white", text_color="red"),
        sg.Text("Mode:"+str(WeaponMode), key='P3', background_color="white", text_color="red"),
        sg.Text("Value:"+str(k_RC_value), key='P4', background_color="white", text_color="red")
        ]]

    window_1 = sg.Window('Window Title', layout_1, alpha_channel=.6, no_titlebar=True, keep_on_top=True,
                         margins=(0, 0), location=(1250, 0), grab_anywhere=True, finalize=True, font=("bold", 10),
                         background_color="white", use_default_focus=False, transparent_color="white")
    window_1.NonBlocking = True


def update_window():
    global IsStateChange
    window_1['P1'].update("Active:" + str(IsSuspensionActive))
    window_1['P2'].update("UI Open:" + str(IsUIOpen))
    window_1['P3'].update("Mode:" + str(WeaponMode))
    window_1['P4'].update("Value:" + str(k_RC_value))
    IsStateChange = False


LS_Mouse = mouse.Listener(on_click=on_click)
LS_Keyboard = keyboard.Listener(on_press=on_press, on_release=on_release)

LS_Mouse.start()
LS_Keyboard.start()

layout_1 = []
window_1 = sg.Window('Window Title')
define_window()
window_1.read(timeout=0)

while True:
    recoil_compensate()
    window_1.read(timeout=0)
    if IsStateChange:
        if WeaponMode == "FullAuto":
            k_RC_value = k_RC_1
        else:
            k_RC_value = k_RC_2
        update_window()

    time.sleep(0.01)
