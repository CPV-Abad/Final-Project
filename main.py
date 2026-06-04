import ctypes, time, psutil, sqlite3
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap import Style
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from winProcess import getForegroundName, isApplication

def main():
    total_time_elapsed = 0
    date_now = datetime.now().strftime("%Y-%m-%d")
    root.geometry("400x300")
    history_button = tk.Button(home_frame, text="Screentime History", command=showHistory)
    history_button.grid(row=0, column=0, columnspan=2, pady=20)
    application = programSelection()
    history_button.destroy()
    for row in query.execute("SELECT * FROM logs WHERE date = ? and application = ?", (date_now, application)):
        total_time_elapsed = total_time_elapsed + row[2]
    timerStart(total_time_elapsed, application, snooze = False)
    main()

def showHistory():
    """Tabulates the recorded screentime history of all applications
    in the database"""
    home_frame.pack_forget()
    root.geometry("750x700")
    timer_text.config(text="Screentime History")
    history_frame = tk.Frame(root)
    history_frame.pack()
    def returnHome():
        history_frame.pack_forget()
        home_frame.pack()
        timer_text.config(text="Program Screen Time")
        root.geometry("400x300")
        root.update()
    table = ttk.Treeview(history_frame, columns = ('app', 'date', 'duration'), show = 'headings')
    table.heading('app', text = 'Application')
    table.heading('date', text = 'Date')
    table.heading('duration', text = 'Total Duration')
    table.pack(fill = 'both', expand = True)
    Screentime_apps = query.execute("SELECT application, date, SUM(duration) FROM logs GROUP BY application, date ORDER BY application ASC")
    
    for app in Screentime_apps:
        table.insert(parent='', index='end', values=(app[0], app[1], timedelta(seconds=app[2])))
        root.update()
    return_home_button = tk.Button(history_frame, text="Home", command=returnHome)
    return_home_button.pack(pady=10)
    return

def timerInstance(application, total_limit, total_time_elapsed):
    """Counts up whenever the application is focused and returns the total 
    time elapsed (seconds) when the time limit is reached"""
    date_now = datetime.now().strftime("%Y-%m-%d")
    timer_text.config(font=("Terminal", 24))
    def stopTimer():
        nonlocal date_now
        nonlocal total_limit
        date_now = datetime.now().strftime("%Y-%m-%d")
        total_limit = -1
    
    time_elapsed = 0
    stop_button = tk.Button(root, text="Stop",command=stopTimer)
    stop_button.pack(pady=20)
    while time_elapsed < total_limit:
        if getForegroundName(ctypes.windll.user32.GetForegroundWindow()) == application:
            time.sleep(1)
            time_elapsed += 1
        timerUpdate(total_time_elapsed, time_elapsed)
    if time_elapsed > 0:
        query.execute("INSERT INTO logs (application, duration, date) VALUES (?, ?, ?)", (application, time_elapsed, date_now))
        query.commit()
    stop_button.destroy()
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
                root.quit()
            else:
                timer_text.config(text="Invalid time limit. Please enter valid time.")
                return
        except ValueError:
            timer_text.config(text="Invalid time limit. Please enter valid time.")
            return
    home_frame.pack_forget()
    input_frame.pack()
    label_guide = tk.Label(input_frame, text="Enter time limit (Hour : Minute : Seconds) ", font=("Arial", 10))
    input_hours = tk.Spinbox(input_frame, from_= 0, to= 23, width=2, font=("Arial", 14))
    input_minutes = tk.Spinbox(input_frame, from_= 0, to= 59, width=2, font=("Arial", 14))
    input_seconds = tk.Spinbox(input_frame, from_= 0, to= 59, width=2, font=("Arial", 14))
    label_guide.grid(row=0, column=0, columnspan=3, pady=10)
    input_hours.grid(row=1, column=0, padx=5, pady=10)
    input_minutes.grid(row=1, column=1, padx=5, pady=10)
    input_seconds.grid(row=1, column=2, padx=5, pady=10)

    start_button = tk.Button(input_frame, text="Start", command=getTimeLimit)
    start_button.grid(row=2, column=0, columnspan=3, pady=20)
    root.mainloop()
    total_limit = total_limit_seconds

    input_hours.destroy()
    input_minutes.destroy()
    input_seconds.destroy()
    start_button.destroy()
    input_frame.pack_forget()

    if total_time_elapsed < total_limit or snooze is True:
        if total_time_elapsed < total_limit and snooze is False:
            total_limit = total_limit - total_time_elapsed
        instance_elapsed = timerInstance(application, total_limit, total_time_elapsed)
        total_time_elapsed = total_time_elapsed + instance_elapsed
        root.attributes("-topmost", True)
        root.update()
        root.attributes("-topmost", False)
        if instance_elapsed == total_limit or total_time_elapsed == total_limit:
            snooze = messagebox.askyesno(title="Snooze", message="Time limit reached.", detail="Would you like to snooze?", parent=root)
        else:
            snooze = False
    else:    
        root.attributes("-topmost", True)
        root.update()
        root.attributes("-topmost", False)
        snooze = messagebox.askyesno(title="Snooze", message="Time limit is already reached.", detail="Would you like to snooze?", parent=root)

    if snooze is True:
        timerStart(total_time_elapsed, application, snooze)

    timer_text.config(text="Program Screen Time", font=("Franklin Gothic Heavy", 24))
    home_frame.pack()
    root.update()
    
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
    program_list = ["SELECT PROGRAM"]
    for program in psutil.process_iter(['pid', 'name']):
        if isApplication(program.info['pid']) and program.info['name'] not in program_list:
            program_list.append(program.info['name'])
    selected_program = tk.StringVar()
    selected_program.set(program_list[0])
    programs_dropdown = ttk.Combobox(home_frame, state="readonly", textvariable=selected_program, width=25, font=("Arial", 10))
    programs_dropdown["values"] = program_list
    programs_dropdown.current(0)
    programs_dropdown.grid(row=1, column=0, padx=10)

    def submitProgram():
        global program_chosen
        program_chosen = selected_program.get()
        if program_chosen != "SELECT PROGRAM":
            root.quit()

    submit_program = tk.Button(home_frame, text="Submit", command=submitProgram)
    submit_program.grid(row=1, column=1)
    root.mainloop()
    submit_program.destroy()
    programs_dropdown.destroy()
    return program_chosen

if __name__ == "__main__":
    root = tk.Tk()
    style = Style(theme="vapor")
    root.title("Program Screen Time")
    timer_text = tk.Label(root, text="PROGRAM SCREEN TIME", font=("Franklin Gothic Heavy", 24))
    timer_text.pack(pady=20)
    home_frame = tk.Frame(root)
    home_frame.columnconfigure(0, weight=5)
    home_frame.columnconfigure(1, weight=1)
    home_frame.rowconfigure((0,1), weight=1)
    home_frame.pack()
    input_frame = tk.Frame(root)
    input_frame.columnconfigure((0,1,2), weight = 2)
    input_frame.rowconfigure((0,1,2), weight = 1)
    query = sqlite3.connect('database.db')
    main()