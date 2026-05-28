import ctypes, time, psutil, sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from winProcess import getForegroundName, isApplication

def main():
    total_time_elapsed = 0
    date_now = datetime.now().strftime("%Y-%m-%d")
    history_button.pack(pady=20)
    application = programSelection()
    history_button.destroy()
    for row in query.execute("SELECT * FROM logs WHERE date = ? and application = ?", (date_now, application)):
        total_time_elapsed = total_time_elapsed + row[2]
    total_time_elapsed = timerStart(total_time_elapsed, application, snooze = False)
    print(total_time_elapsed)
    print("Total time elapsed: " + str(total_time_elapsed) + " seconds")
    main()

def showHistory():
    history_button.destroy()
    table = ttk.Treeview(root, columns = ('app', 'date', 'duration'), show = 'headings')
    table.heading('app', text = 'Application')
    table.heading('date', text = 'Date')
    table.heading('duration', text = 'Total Duration')
    table.pack(fill = 'both', expand = True)
    Screentime_apps = query.execute("SELECT application, date, SUM(duration) FROM logs GROUP BY application, date ORDER BY application ASC")
    
    for app in Screentime_apps:
        table.insert(parent='', index='end', values=(app[0], app[1], app[2]))
        root.update()
    return

def timerInstance(application, total_limit, total_time_elapsed):
    """Counts up whenever the application is focused and returns the total time elapsed (seconds) when the time limit is reached"""
    date_now = datetime.now().strftime("%Y-%m-%d")
    time_elapsed = 0
    while time_elapsed < total_limit:
        if getForegroundName(ctypes.windll.user32.GetForegroundWindow()) == application:
            time.sleep(1)
            time_elapsed += 1
            print(time_elapsed)
        timerUpdate(total_time_elapsed, time_elapsed)
    if time_elapsed > 0:
        query.execute("INSERT INTO logs (application, duration, date) VALUES (?, ?, ?)", (application, time_elapsed, date_now))
        query.commit()
    return time_elapsed

def timerStart (total_time_elapsed, application, snooze):
    """Initializes the timer """
    def getTimeLimit():
        try:
            global total_limit_seconds
            limit_hours = int(input_hours.get())
            limit_minute = int(input_minutes.get())
            limit_seconds = int(input_seconds.get())
            
            if limit_hours < 24 and limit_minute < 60 and limit_seconds < 60:
                total_limit_seconds = (limit_hours * 3600) + (limit_minute * 60) + limit_seconds
                print(total_limit_seconds)
                root.quit()
            else:
                timer_text.config(text="Invalid time limit. Please enter valid time.")
                return
        except ValueError:
            timer_text.config(text="Invalid time limit. Please enter valid time.")
            return

    input_hours = tk.Entry(root)
    input_minutes = tk.Entry(root)
    input_seconds = tk.Entry(root)
    input_minutes = tk.Entry(root)
    input_hours.pack(pady=10)
    input_minutes.pack(pady=10)
    input_seconds.pack(pady=10)
    
    submit_limit = tk.Button(root, text="Submit", command=getTimeLimit)
    submit_limit.pack(pady=20)
    root.mainloop()
    total_limit = total_limit_seconds

    input_hours.destroy()
    input_minutes.destroy()
    input_seconds.destroy()
    submit_limit.destroy()


    if total_time_elapsed < total_limit or snooze is True:
        if total_time_elapsed < total_limit and snooze is False:
            total_limit = total_limit - total_time_elapsed
        total_time_elapsed = total_time_elapsed + timerInstance(application, total_limit, total_time_elapsed)
        root.attributes("-topmost", True)
        root.update()
        root.attributes("-topmost", False)
        snooze = messagebox.askyesno(title="Snooze", message="Time limit reached.", detail="Would you like to snooze?", parent=root)
    else:    
        root.attributes("-topmost", True)
        root.update()
        root.attributes("-topmost", False)
        snooze = messagebox.askyesno(title="Snooze", message="Time limit is already reached.", detail="Would you like to snooze?", parent=root)

    if snooze is True:
        timerStart(total_time_elapsed, application, snooze)
    return total_time_elapsed

def timerUpdate(total_time_elapsed, time_elapsed):
    """Updates the timer text on the GUI"""
    current_time_elapsed = total_time_elapsed + time_elapsed
    hours_elapsed = current_time_elapsed // 3600
    minutes_elapsed = (current_time_elapsed % 3600) // 60
    second_elapsed = current_time_elapsed % 60
    timer_text.config(text= str(hours_elapsed).zfill(2) + " : " + str(minutes_elapsed).zfill(2) + " : " + str(second_elapsed).zfill(2))
    root.update()

def programSelection():
    """Lists all the currently running programs"""
    program_list = []
    for program in psutil.process_iter(['pid', 'name']):
        if isApplication(program.info['pid']) and program.info['name'] not in program_list:
            program_list.append(program.info['name'])
    selected_program = tk.StringVar()
    selected_program.set("SELECT PROGRAM")
    programs_dropdown = tk.OptionMenu(root, selected_program, *program_list)
    programs_dropdown.pack(pady=20)

    def submitProgram():
        global program_chosen
        program_chosen = selected_program.get()
        if program_chosen != "SELECT PROGRAM":
            print(program_chosen)
            root.quit()

    submit_program = tk.Button(root, text="Submit", command=submitProgram)
    submit_program.pack(pady=20)
    root.mainloop()
    submit_program.destroy()
    programs_dropdown.destroy()
    return program_chosen


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Program Screen Timer")
    root.geometry("800x600")
    timer_text = tk.Label(root, text="Program Screen Timer", font=("Arial", 24))
    timer_text.pack(pady=20)
    history_button = tk.Button(root, text="Screentime History", command=showHistory)
    query = sqlite3.connect('database.db')
    main()