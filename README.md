# Program Timer
#### Description:
A Python application that acts as a timer for a program of a user's choice. It also keeps logs of the instances whenever the timer is initiated, which may help the user keep track of their screentime with the specified programs.

## Functionalities:

### Timer:
Essentially, this application works like a timer where the user specifies a time limit but for a certain program. Once the timer has been started, the application will count the time elapsed whenever the window of the selected program is in focus, up until the time limit has been reached or the timer has been manually stopped. If the time limit has been reached, the user will be prompted to either snooze or end the timer. When snoozed, the user will then be asked to enter an additional time limit. _Note that the elapsed time of each timer instance of a specified program within the day will be considered in initially starting the timer_.

### Screentime History:
The application keeps track of the user's daily screentime per application by logging each timer instance to an SQL database. The user can preview these logs by pressing the "See Screentime History" button, then selecting the program whose screentime history they want to preview.

## Requirements:
+ Python3
+ Sqlite3
+ Psutils
+ Pygame
+ Pywin32
+ Tkinter
+ Ttkbootstrap

## How to use program:
### Downloading and running the program:
1. Install all requirements as enumerated in the previous section.
2. Download the program by running this command in your terminal: __git clone https://github.com/CPV-Abad/Final-Project.git__ or by manually downloading all files from the main branch
3. Navigate to where the files are downloaded then run py main.py in your terminal

### Timer:
1. Select your desired application to time via the dropdown menu and pressing the submit button. _The application must be running in order for this program to include it from the selection._
2. Enter a time limit, formatted as _HH:MM:SS_.
3. Press start and wait until designated time limit has been reached. Alternatively, manually stop the timer.
4. If the time limit has been reached, choose whether to snooze or stop the timer.
5. If snoozed repeat step until program has been stopped.

#### Screentime History page
1. Press the "See Screentime History" button from the home menu
2. Select a program from the menu and press the "Show History" button
3. The total daily screentime duration would be displayed, sorted by date.
4. Repeat step 2 to select a different program.
5. Press the "Home" button to return to the home menu.
