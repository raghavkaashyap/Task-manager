Python Task Manager!

This project is a task management tool designed to help users organize their weekly schedules. Built using Python and the Tkinter library for the GUI, the program allows users to input task details such as the task name, duration (in hours), and deadline. The program then generates a schedule in a tabular format, showing the time allocated for each task throughout the week to ensure timely completion. Additionally, the program can send email reminders to users about their upcoming tasks.

LIMITATIONS: 
1) The deadline entered should preferably be within one week from the current date.
2) The source code for the program has only been tested on Python3, so make sure to use Python3 while running the program.
3) The source code has been extensively tested on Windows, but not on macOS or other platforms.

ADDITIONAL NOTES:
1) Fonts used in the source code (lines 241 and 246) are native Windows fonts. The source code may be used on other platforms after downloading lucida_calligraphy_italic.ttf and BASKE1.ttf, commenting out lines 241 and 246, and uncommenting lines 242, 245, and 247. Bear in mind that when these files are downloaded, the user must store the file path in a string (file_path: line 245) and update lines 242 and 247 accordingly. 
