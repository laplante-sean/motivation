'''
Windows methods for enabling/disabling a controller
'''
import win32com.client

shell = win32com.client.Dispatch("WScript.Shell")


def win32_disable_controller():
    shell.SendKeys(" ", 0)


def win32_enable_controller():
    raise NotImplementedError
