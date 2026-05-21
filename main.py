import ctypes, time, win32process, wmi


def main():
    application = input("Enter which application you want to time: ")
    total_time_elapsed = 0
    snooze = 'y'
    while snooze == 'y':
        total_time_elapsed = timerStart(total_time_elapsed, application)
        snooze = input("Would you like to snooze? (y/n):")
    print("Total time elapsed: " + str(total_time_elapsed) + " seconds")


def getAppName(hwnd):
    c = wmi.WMI()
    exe = None
    try:
        _, process_id = win32process.GetWindowThreadProcessId(hwnd)
        for program in c.query('SELECT Name FROM Win32_Process WHERE ProcessId = %s' % str(process_id)):
            print(program.Name)
            exe = program.Name
            break
    except:
        return None
    else:
        return exe

def screenTime(application, total_limit_seconds):
    time_elapsed = 0
    while time_elapsed < total_limit_seconds:
        if getAppName(ctypes.windll.user32.GetForegroundWindow()) == application:
            time.sleep(1)
            time_elapsed += 1
            print(time_elapsed)
    return time_elapsed

def timerStart (total_time_elapsed, application):
    limit_hours = int(input("Enter time limit(hours): "))
    limit_minute = int(input("Enter time limit(minutes): "))
    limit_seconds = int(input("Enter time limit(seconds): "))
    total_limit_seconds = (limit_hours * 3600) + (limit_minute * 60) + limit_seconds
    total_time_elapsed = total_time_elapsed + screenTime(application + ".exe", total_limit_seconds)
    print("Time limit reached")
    return total_time_elapsed

main()