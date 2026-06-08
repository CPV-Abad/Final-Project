import ctypes, psutil, sqlite3, time
import tkinter as tk
import ttkbootstrap as ttk
from datetime import datetime, timedelta
from pygame import mixer
from ttkbootstrap import Style
from tkinter import messagebox
from winProcess import getForegroundName, isApplication

def main():
    """Main Function"""
    # Initialize variables
    total_time_elapsed = 0
    date_now = datetime.now().strftime("%Y-%m-%d")
    
    # Set GUI dimension for home frame
    root.geometry("400x250")

    # Initialize button to access history page
    history_button = tk.Button(home_frame, text="See Screentime History", command=showHistory)
    history_button.grid(row=0, column=0, columnspan=2, pady=20)

    # Check for selected programs
    application = programSelection()

    # Remove history button
    history_button.destroy()

    # Get total elapsed time of the selected program for the current date
    for row in query.execute("SELECT * FROM logs WHERE date =? and application =?", (date_now, application)):
        total_time_elapsed = total_time_elapsed + row[2]
    
    # Begin timer
    timerStart(total_time_elapsed, application, snooze = False)

    # Loop main once timer is done
    main()

def showHistory():
    """Tabulates the recorded screentime of Selected applications
    from the database"""

    # Acquire all applications from the database
    app_list = ["SELECT PROGRAM"]
    for program in query.execute("SELECT DISTINCT application FROM logs"):
        app_list.append(program[0])

    # Remove home frame
    home_frame.pack_forget()
    
    # Initialize history frame and widgets
    root.geometry("750x700")
    timer_text.config(text="SCREENTIME HISTORY")
    history_frame = tk.Frame(root)
    history_frame.columnconfigure((0,1), weight=1)
    history_frame.rowconfigure((0,2), weight=1)
    history_frame.rowconfigure((1), weight=5)
    history_frame.pack()
    selected_app = tk.StringVar()

    # Initialize dropdown menu for selecting program
    programs_dropdown = ttk.Combobox(history_frame, state="readonly", textvariable=selected_app, width=25, font=("Arial", 10))
    programs_dropdown["values"] = app_list
    programs_dropdown.current(0)
    programs_dropdown.grid(row=0, column=0, padx=10, pady=10)

    def returnHome():
        """ Returns to home frame when return home button is pressed"""
        history_frame.pack_forget()
        home_frame.pack()
        timer_text.config(text="PROGRAM TIMER")
        root.geometry("400x300")
        root.update()

    def submitProgram():
        """Tabulate the date and duration of the selected application
        from the database"""
        global app_selected

        # Clear table
        for entry in table.get_children():
            table.delete(entry)

        if selected_app.get() != "SELECT PROGRAM":
            app_selected = selected_app.get()
            Screentime_data = query.execute("SELECT date, SUM(duration) FROM logs WHERE application =? GROUP BY date", (app_selected,))

            # Populate table with new data
            for row in Screentime_data:
                table.insert(parent="", index="end", values=(row[0], timedelta(seconds=row[1])))
                root.update()

    # Initialize Submit button
    submit_program = tk.Button(history_frame, text="Show History", command=submitProgram)
    submit_program.grid(row=0, column=1, padx=10, pady=10)

    # Initialize table
    table = ttk.Treeview(history_frame, columns=("date", "duration"), height=25, show="headings")
    table.heading("date", text = "Date")
    table.heading("duration", text = "Total Duration")
    table.column("date", width=300, minwidth=300, anchor="center", stretch=False)
    table.column("duration", width=300, minwidth=300, anchor="center", stretch=False)
    scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)
    table.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
    scrollbar.grid(row=1, column=2, sticky="ns")

    # Initialize button to return to home frame
    return_home_button = tk.Button(history_frame, text="Home", command=returnHome)
    return_home_button.grid(row=2, column=0, columnspan=2, pady=20)
    return

def timerInstance(application, total_limit, total_time_elapsed):
    """Counts up whenever the application is focused and returns the total 
    time elapsed (seconds) when the time limit is reached or timer is
    stoppped manually"""

    # Initialize variable and constant
    date_now = datetime.now().strftime("%Y-%m-%d")
    TIMERSTOPPED = -1
    timer_text.config(font=("Terminal", 24))

    def stopTimer():
        """Manually stop timer when stop button is pressed"""
        nonlocal date_now
        nonlocal total_limit
        date_now = datetime.now().strftime("%Y-%m-%d")
        # 
        total_limit = TIMERSTOPPED

    # Reset elapsed time for current instance
    time_elapsed = 0

    # Initialize stop button
    stop_button = tk.Button(root, text="Stop",command=stopTimer)
    stop_button.pack(pady=20)

    # Count up for every second that passes while program is focused
    while time_elapsed < total_limit:
        # Check if selected program is focused
        if getForegroundName(ctypes.windll.user32.GetForegroundWindow()) == application:
            time.sleep(1)
            time_elapsed += 1
        # Update timer GUI
        timerUpdate(total_time_elapsed, time_elapsed)

    # Record time elapsed if it is greater than 0
    if time_elapsed > 0:
        query.execute("INSERT INTO logs (application, duration, date) VALUES (?, ?, ?)", (application, time_elapsed, date_now))
        query.commit()
    
    # Return time elapsed for current instance
    stop_button.destroy()
    return time_elapsed

def timerStart (total_time_elapsed, application, snooze):
    """Initializes the timer """
    def getTimeLimit():
        """Acquire time limit once start button is pressed"""
        try:
            global total_limit_seconds
            limit_hours = int(input_hours.get())
            limit_minute = int(input_minutes.get())
            limit_seconds = int(input_seconds.get())
            
            # Check if format is valid
            if limit_hours < 24 and limit_minute < 60 and limit_seconds < 60:
                # Get sum of input in seconds
                total_limit_seconds = (limit_hours * 3600) + (limit_minute * 60) + limit_seconds
                root.quit()
            else:
                timer_text.config(text="Invalid time limit. Please enter valid time.")
                return
        except ValueError:
            timer_text.config(text="Invalid time limit. Please enter valid time.")
            return
    
    # Hide home frame and show input frame
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

    # Loop until start button is pressed
    root.mainloop()
    total_limit = total_limit_seconds

    # Remove input frame
    input_hours.destroy()
    input_minutes.destroy()
    input_seconds.destroy()
    start_button.destroy()
    input_frame.pack_forget()

    # Check if time limit has been reached or timer was snoozed
    if total_time_elapsed < total_limit or snooze is True:
        if total_time_elapsed < total_limit and snooze is False:
            total_limit = total_limit - total_time_elapsed
        instance_elapsed = timerInstance(application, total_limit, total_time_elapsed)
        total_time_elapsed = total_time_elapsed + instance_elapsed

        # Ask user if timer should be snoozed
        if instance_elapsed == total_limit or total_time_elapsed == total_limit:
            root.attributes("-topmost", True)
            root.update()
            mixer.music.load("alarm.mp3")
            mixer.music.play(loops=3)
            snooze = messagebox.askyesno(title="Snooze", message="Time limit reached.", detail="Would you like to snooze?", parent=root)
            mixer.music.stop()
        else:
            snooze = False
    else:    
        # Ask user if timer should be snoozed
        root.attributes("-topmost", True)
        root.update()
        mixer.music.load("alarm.mp3")
        mixer.music.play(loops=3)
        snooze = messagebox.askyesno(title="Snooze", message="Time limit is already reached.", detail="Would you like to snooze?", parent=root)
        mixer.music.stop()

    # Disable pop-up
    root.attributes("-topmost", False)

    # Reset timer if snoozed
    if snooze is True:
        timerStart(total_time_elapsed, application, snooze)

    # Return to home frame
    timer_text.config(text="PROGRAM TIMER", font=("Franklin Gothic Heavy", 24))
    home_frame.pack()
    root.update()
    
    return total_time_elapsed

def timerUpdate(total_time_elapsed, time_elapsed):
    """Updates the timer text on the GUI"""
    # Current time elapsed calculation
    current_time_elapsed = total_time_elapsed + time_elapsed
    hours_elapsed = current_time_elapsed // 3600
    minutes_elapsed = (current_time_elapsed % 3600) // 60
    second_elapsed = current_time_elapsed % 60
    
    # Update GUI text
    timer_text.config(text= str(hours_elapsed).zfill(2) + " : " + str(minutes_elapsed).zfill(2) + " : " + str(second_elapsed).zfill(2))
    root.update()

def programSelection():
    """Lists all the currently running programs"""
    # initialize program list variable
    program_list = ["SELECT PROGRAM"]

    def updateProgramlist():
        """List all running non-background program in the dropdown menu"""
        nonlocal program_list

        # Iterate over running processes
        for program in psutil.process_iter(["pid", "name"]):
            # Append process to program list if it has a window handle
            if isApplication(program.info["pid"]) and program.info["name"] not in program_list:
                program_list.append(program.info["name"])
        
        # Update choices in drop down menu
        programs_dropdown["values"] = program_list

    def submitProgram():
        """Submit program from dropdown menu"""
        global program_chosen
        program_chosen = selected_program.get()
        if program_chosen != "SELECT PROGRAM":
            root.quit()

    # Initialize program selection widgets
    selected_program = tk.StringVar()
    programs_dropdown = ttk.Combobox(home_frame, state="readonly", textvariable=selected_program, postcommand=updateProgramlist, width=25, font=("Arial", 10))
    programs_dropdown["values"] = program_list
    programs_dropdown.current(0)
    programs_dropdown.grid(row=1, column=0, padx=10)
    submit_program = tk.Button(home_frame, text="Submit", command=submitProgram)
    submit_program.grid(row=1, column=1)
    
    # Loop until program has been selected
    root.mainloop()

    # Hide program Selection widgets
    submit_program.destroy()
    programs_dropdown.destroy()
    return program_chosen

if __name__ == "__main__":
    # Initialize GUI
    root = tk.Tk()
    style = Style(theme="vapor")
    root.title("Program Timer")
    timer_text = tk.Label(root, text="PROGRAM TIMER", font=("Franklin Gothic Heavy", 24))
    mixer.init()
    timer_text.pack(pady=20)

    # Initialize Home Frame
    home_frame = tk.Frame(root)
    home_frame.columnconfigure(0, weight=5)
    home_frame.columnconfigure(1, weight=1)
    home_frame.rowconfigure((0,1), weight=1)
    home_frame.pack()
    input_frame = tk.Frame(root)
    input_frame.columnconfigure((0,1,2), weight = 2)
    input_frame.rowconfigure((0,1,2), weight = 1)

    # Connect to database
    query = sqlite3.connect('database.db')

    # Start main
    main()