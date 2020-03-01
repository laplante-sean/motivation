'''
OS Agnostive controller disabling functionality
'''
import os


def disable_controller():
    '''
    Disabled the controller
    '''
    if os.name == "nt":
        from motivation.controller.win32 import win32_disable_controller
        win32_disable_controller()
    else:
        from motivation.controller.unix import unix_disable_controller
        unix_disable_controller()


def enable_controller():
    '''
    Re-enables the controller
    '''
    if os.name == "nt":
        from motivation.controller.win32 import win32_enable_controller
        win32_enable_controller()
    else:
        from motivation.controller.unix import unix_enable_controller
        unix_enable_controller()
