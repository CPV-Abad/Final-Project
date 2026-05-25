import ctypes, time, win32process, wmi, sqlite3
from datetime import datetime

query = sqlite3.connect('database.db')


def main():
    total_time_elapsed = 0
    date_now = datetime.now().strftime("%Y-%m-%d")
    application = input("Enter which application you want to time: ")
    for row in query.execute("SELECT * FROM logs WHERE date = ? and application = ?", (date_now, application + ".exe")):
        total_time_elapsed = total_time_elapsed + row[2]
    total_time_elapsed = timerStart(total_time_elapsed, application, snooze='n')
    print("Total time elapsed: " + str(total_time_elapsed) + " seconds")


def getAppName(hwnd):
    """Acquire the name of the executables that are currently running""""
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
    """Counts up whenever the application is focused and returns the total time elapsed (seconds) when the time limit is reached"""
    date_now = datetime.now().strftime("%Y-%m-%d")
    time_elapsed = 0
    while time_elapsed < total_limit_seconds:
        if getAppName(ctypes.windll.user32.GetForegroundWindow()) == application:
            time.sleep(1)
            time_elapsed += 1
            print(time_elapsed)
    if time_elapsed > 0:
        query.execute("INSERT INTO logs (application, duration, date) VALUES (?, ?, ?)", (application, time_elapsed, date_now))
        query.commit()
    return time_elapsed

def timerStart (total_time_elapsed, application, snooze):
    """Initializes the timer """
    limit_hours = int(input("Enter time limit(hours): "))
    limit_minute = int(input("Enter time limit(minutes): "))
    limit_seconds = int(input("Enter time limit(seconds): "))
    total_limit_seconds = (limit_hours * 3600) + (limit_minute * 60) + limit_seconds

    if total_time_elapsed < total_limit_seconds or snooze == 'y':
        if total_time_elapsed < total_limit_seconds:
            total_limit_seconds = total_limit_seconds - total_time_elapsed
        total_time_elapsed = total_time_elapsed + screenTime(application + ".exe", total_limit_seconds)
        snooze = input("Time limit reached, would you like to snooze? (y/n):")
    else:    
        snooze = input("Time limit already reached, would you like to snooze? (y/n):")

    if snooze == 'y':
        timerStart(total_time_elapsed, application, date_now, snooze)
    else:
        return total_time_elapsed

main()