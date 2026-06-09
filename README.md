# Program timer
#### Video Demo:  <URL HERE>
#### Description:
A python application that acts as a timer for a program of a user's choice. It also keeps logs of the instances whenever the timer is initiated, which may help the user keep track of their screentime with the specified programs. 

## Functionalities:

### Timer:
Essentially, this application works like a timer where the user specifies a program and a time limit. Once the timer has been started, the applicationn will count the time elapsed whenever the window of the selected program is in focus, up until the time limit has been reached or the timer has been manually stopped. If the time limit has been reached, the user will be prompted to either snooze or end the timer. When snoozed, the user will then be asked to enter an additional time limit. _Note that the elapsed time of each timer instance of a specified prorgam within the day will be considered in initially starting the timer_.

### Screentime History:
The application keeps track of the users daily screentime per application by logging each timer instance to an SQL database. The user can preview these logs by pressing the "See Screentime History" button, then selecting the program whose screentime history they wanted to preview.

## Requirements:
+ Python3
+ Sqlite3
+ Psutils
+ Pywin32
+ Pyame
+ tkinter
+ ttkbootstrap

