import win32gui, psutil, win32process, ctypes

def getForegroundName(hwnd):
    """Acquire the name of the executables that are currently running"""
    exe = None
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for program in psutil.process_iter(['pid', 'name']):
            if program.info['pid'] == pid:
                print(program.info['name'])
                exe = program.info['name']
                break
    except:
        return None
    else:
        return exe

def isApplication(pid):
    """
    Checks if a given Process ID belongs to a visible application
    rather than a background process.
    """
    try:
        # Check if the process has any window handles associated with it
        windows = []
        def enumerateWindows(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == extra:
                    windows.append(hwnd)
            return True

        win32gui.EnumWindows(enumerateWindows, pid)
        
        # If it has a visible window and a title, it's an application
        for hwnd in windows:
            if win32gui.GetWindowText(hwnd):
                return True
    except Exception:
        pass
    return False
