import math
from tkinter import *
from tkcalendar import DateEntry
from PIL import ImageTk, Image, ImageFont, ImageDraw
from io import BytesIO
import datetime
import smtplib
import json

task_entry_labels = ['Task Name', 'Task Duration (Hours)']
task_deadline_label = 'Deadline (Date)'
missing_values_warning_message = "You must enter values for all the fields"
invalid_type_duration_message = "Please enter duration in Number of hours"
invalid_type_name_message = "Please enter an alphanumeric Task Name"

weekly_allocated_hrs = {}  # dictionary to maintain hours allocated by task for each day of the week
days_of_the_week = []  # list that maintains days of the week starting from current day


def allot_time(duration, deadline):  # function calculates remaining time(days) and allots time needed per day
    y = int(deadline[0:4])
    m = int(deadline[5:7])
    d = int(deadline[8:])

    deadline = datetime.datetime(y, m, d, 23, 59, 59)  # deadline is 23:59:59 on the date specified
    time_to_deadline_in_hrs = get_remaining_time_to_deadline_in_hrs(deadline)

    time_to_deadline_in_days = math.ceil(time_to_deadline_in_hrs / 24)
    if time_to_deadline_in_days == 0:
        time_to_deadline_in_days = 1
    hours_allotted_per_day = round(int(duration) / time_to_deadline_in_days)
    daily_allocation = {}
    for i in range(time_to_deadline_in_days - 1):
        daily_allocation[days_of_the_week[i]] = hours_allotted_per_day
    if hours_allotted_per_day * (time_to_deadline_in_days - 1) < int(duration):
        daily_allocation[days_of_the_week[time_to_deadline_in_days - 1]] = int(duration) - hours_allotted_per_day * (
            time_to_deadline_in_days - 1)
    return daily_allocation


def get_remaining_time_to_deadline_in_hrs(deadline):
    current_time = datetime.datetime.now()
    remaining_time_to_deadline = deadline - current_time
    time_to_deadline_in_hrs = round(remaining_time_to_deadline.total_seconds() / 3600)
    return time_to_deadline_in_hrs


def is_entered_data_valid(entries, warning_lbl=None):
    valid_data = True
    # dur = 0
    for entry in entries:
        if len(entry[1].get()) > 0:
            if entry[0] == "Task Duration (Hours)":
                if entry[1].get().isdigit():
                    continue
                else:  # if Task Duration is not numeric, display a warning
                    warning_lbl.config(text=invalid_type_duration_message)
                    valid_data = False
                    break

            elif entry[0] == "Task Name":
                for i in range(len(entry[1].get())):
                    if entry[1].get()[i].isalnum() or entry[1].get()[i].isspace():
                        continue
                    else:  # if Task Name is not alphanumeric, display a warning
                        warning_lbl.config(text=invalid_type_name_message)
                        valid_data = False
                        break
            elif entry[0] == "Deadline (Date)":

                year = int(entry[1].get()[:4])
                month = int(entry[1].get()[5:7])
                day = int(entry[1].get()[8:])
                deadline = datetime.datetime(year, month, day, 23, 59, 59)
                task_duration_hours = int(entries[1][1].get())
                if get_remaining_time_to_deadline_in_hrs(deadline) < task_duration_hours:
                    warning_lbl.config(
                        text="Too less time to finish task. Please extend the deadline or reduce the task duration")
                    valid_data = False
                    break

            continue

        else:  # if all fields are not filled out, display a warning
            warning_lbl.config(text=missing_values_warning_message)
            valid_data = False
            break
    if valid_data:
        warning_lbl.config(text='')
    return valid_data


'''
Update the hours allocated by tasks for each day of the week in the weekly_allocated_hrs dictionary based on the
allocations determined by the allot_time method
'''
def update_weekly_allocation(task_name, task_schedule):
    for day in task_schedule:
        daily_hours = {task_name: task_schedule.get(day)}
        weekly_allocated_hrs.get(day).update(daily_hours)


def store_task_details(entries):
    global task_file
    # warning_label.config(text='')
    if is_entered_data_valid(entries, warning_label):
        c = 0
        for entry in entries:
            # field = entry[0]
            text = entry[1].get()
            if c == 0:
                task_name = text
                c += 1
            elif c == 1:
                duration = text
                c += 1
            elif c == 2:
                deadline = text
                allocation = allot_time(duration, deadline)
                update_weekly_allocation(task_name, allocation)
                print(weekly_allocated_hrs)

            task_file.write('{},'.format(text))
            task_file.flush()  # write the task details to the task_file
            if len(text) > 0:
                entry[1].delete(0, END)

        task_file.write('\n')  # write a new line after each record is written to the file


def display_form(root, labels):
    entries = []
    for task_box_label in labels:  # loop through the task labels, create entries and add them to a list
        row = Frame(root)
        label = Label(row, width=15, text=task_box_label, anchor='w')
        entry = Entry(row)
        row.pack(side=TOP, fill=X, padx=5, pady=5)
        label.pack(side=LEFT)
        entry.pack(side=RIGHT, expand=YES, fill=X)
        entries.append((task_box_label, entry))

    # Show date picker for Task Deadline, get the date from it and add to the list of entries
    row = Frame(root)
    label = Label(row, width=15, text=task_deadline_label, anchor='w')
    cal = DateEntry(row, selectmode='day', date_pattern='yyyy-mm-dd')
    row.pack(side=TOP, fill=X, padx=5, pady=5)
    label.pack(side=LEFT)
    cal.pack(side=RIGHT, expand=YES, fill=X)
    entries.append((task_deadline_label, cal))
    return entries


def value_entry():
    entries = display_form(root, task_entry_labels)
    root.bind('<Return>', (lambda event, e=entries: store_task_details(e)))
    b1 = Button(root, text='Submit', bg="yellow", fg="green", command=(lambda e=entries: store_task_details(e)))
    b1.pack(side=LEFT, padx=100, pady=10)

    b2 = Button(root, text='Quit', fg="red", command=root.destroy)
    b2.pack(side=LEFT, padx=5, pady=10)


def gen_button():
    global m

    m.title('Task Scheduler')
    gen_button = Button(m, text='GENERATE SCHEDULE', background='cyan', activebackground='lime', width=20, height=5,
                        command=lambda: table_create_and_hide(gen_button))
    gen_button.grid()

    for i in range(3):
        m.columnconfigure(i, weight=1)
    for i in range(8):
        m.rowconfigure(i, weight=1)
    m.mainloop()


def table_create_and_hide(button):
    with open('weekly_schedule.json', 'w') as convert_file:
        convert_file.write(json.dumps(weekly_allocated_hrs, indent=4))
    table_create()
    button.grid_forget()


def table_create():
    global m
    global weekly_allocated_hrs
    global days_of_the_week

    image_directory = '.\\Images\\' # Images in the image folder
    img10 = Image.open(image_directory + 'day.png')
    img20 = Image.open(image_directory + 'day1.jpg')
    img30 = Image.open(image_directory + 'day2.png')
    img40 = Image.open(image_directory + 'day3.png')
    img50 = Image.open(image_directory + 'day4.png')
    img60 = Image.open(image_directory + 'day5.png')
    img70 = Image.open(image_directory + 'day6.png')
    img1 = Image.open(image_directory + 'task.png')
    img2 = Image.open(image_directory + 'task1.jpg')
    img3 = Image.open(image_directory + 'task2.png')
    img4 = Image.open(image_directory + 'task3.png')
    img5 = Image.open(image_directory + 'task4.png')
    img6 = Image.open(image_directory + 'task5.png')
    img7 = Image.open(image_directory + 'task6.png')
    img01 = Image.open(image_directory + 'time.png')
    img02 = Image.open(image_directory + 'time1.jpg')
    img03 = Image.open(image_directory + 'time2.png')
    img04 = Image.open(image_directory + 'time3.png')
    img05 = Image.open(image_directory + 'time4.png')
    img06 = Image.open(image_directory + 'time5.png')
    img07 = Image.open(image_directory + 'time6.png')

    task_cell_width = 300
    task_cell_height = 100
    day_cell_width = 200
    day_cell_height = 100
    schedule_cell_width = 200
    schedule_cell_height = 100
    img1 = img1.resize((task_cell_width, task_cell_height), Image.Resampling.LANCZOS)
    img2 = img2.resize((task_cell_width, task_cell_height), Image.Resampling.LANCZOS)
    img3 = img3.resize((task_cell_width, task_cell_height), Image.Resampling.LANCZOS)
    img4 = img4.resize((task_cell_width, task_cell_height), Image.Resampling.LANCZOS)
    img5 = img5.resize((task_cell_width, task_cell_height), Image.Resampling.LANCZOS)
    img6 = img6.resize((task_cell_width, task_cell_height), Image.Resampling.LANCZOS)
    img7 = img7.resize((task_cell_width, task_cell_height), Image.Resampling.LANCZOS)
    img10 = img10.resize((day_cell_width, day_cell_height), Image.Resampling.LANCZOS)
    img20 = img20.resize((day_cell_width, day_cell_height), Image.Resampling.LANCZOS)
    img30 = img30.resize((day_cell_width, day_cell_height), Image.Resampling.LANCZOS)
    img40 = img40.resize((day_cell_width, day_cell_height), Image.Resampling.LANCZOS)
    img50 = img50.resize((day_cell_width, day_cell_height), Image.Resampling.LANCZOS)
    img60 = img60.resize((day_cell_width, day_cell_height), Image.Resampling.LANCZOS)
    img70 = img70.resize((day_cell_width, day_cell_height), Image.Resampling.LANCZOS)
    img01 = img01.resize((schedule_cell_width, schedule_cell_height), Image.Resampling.LANCZOS)
    img02 = img02.resize((schedule_cell_width, schedule_cell_height), Image.Resampling.LANCZOS)
    img03 = img03.resize((schedule_cell_width, schedule_cell_height), Image.Resampling.LANCZOS)
    img04 = img04.resize((schedule_cell_width, schedule_cell_height), Image.Resampling.LANCZOS)
    img05 = img05.resize((schedule_cell_width, schedule_cell_height), Image.Resampling.LANCZOS)
    img06 = img06.resize((schedule_cell_width, schedule_cell_height), Image.Resampling.LANCZOS)
    img07 = img07.resize((schedule_cell_width, schedule_cell_height), Image.Resampling.LANCZOS)

    file = open('C:\Windows\Fonts\LCALLIG.TTF','rb')
    #file = open(image_directory + 'lucida_calligraphy_italic.ttf', 'rb')
    fnt = BytesIO(file.read())
    textfont = ImageFont.truetype(fnt, 15)

    file2 = open('C:\Windows\Fonts\BASKVILL.TTF','rb')
   #file2 = open(image_directory + 'BASKE1.ttf', 'rb')
    fnt2 = BytesIO(file2.read())
    textfont2 = ImageFont.truetype(fnt2, 15)

    edit1 = ImageDraw.Draw(img1)
    edit2 = ImageDraw.Draw(img2)
    edit3 = ImageDraw.Draw(img3)
    edit4 = ImageDraw.Draw(img4)
    edit5 = ImageDraw.Draw(img5)
    edit6 = ImageDraw.Draw(img6)
    edit7 = ImageDraw.Draw(img7)

    edit10 = ImageDraw.Draw(img10)
    edit20 = ImageDraw.Draw(img20)
    edit30 = ImageDraw.Draw(img30)
    edit40 = ImageDraw.Draw(img40)
    edit50 = ImageDraw.Draw(img50)
    edit60 = ImageDraw.Draw(img60)
    edit70 = ImageDraw.Draw(img70)

    edit01 = ImageDraw.Draw(img01)
    edit02 = ImageDraw.Draw(img02)
    edit03 = ImageDraw.Draw(img03)
    edit04 = ImageDraw.Draw(img04)
    edit05 = ImageDraw.Draw(img05)
    edit06 = ImageDraw.Draw(img06)
    edit07 = ImageDraw.Draw(img07)

    # Use the generated days of the week to populate the table
    day_text_x = 50
    day_text_y = 35
    edit10.text((day_text_x, day_text_y), days_of_the_week[0], ('white'), font=textfont)
    edit20.text((day_text_x, day_text_y), days_of_the_week[1], ('white'), font=textfont)
    edit30.text((day_text_x, day_text_y), days_of_the_week[2], ('white'), font=textfont)
    edit40.text((day_text_x, day_text_y), days_of_the_week[3], ('white'), font=textfont)
    edit50.text((day_text_x, day_text_y), days_of_the_week[4], ('white'), font=textfont)
    edit60.text((day_text_x, day_text_y), days_of_the_week[5], ('white'), font=textfont)
    edit70.text((day_text_x, day_text_y), days_of_the_week[6], ('white'), font=textfont)

    img10 = ImageTk.PhotoImage(img10)
    img20 = ImageTk.PhotoImage(img20)
    img30 = ImageTk.PhotoImage(img30)
    img40 = ImageTk.PhotoImage(img40)
    img50 = ImageTk.PhotoImage(img50)
    img60 = ImageTk.PhotoImage(img60)
    img70 = ImageTk.PhotoImage(img70)

    L_day1 = Label(m, image=img10, borderwidth=0)
    L_day2 = Label(m, image=img20, borderwidth=0)
    L_day3 = Label(m, image=img30, borderwidth=0)
    L_day4 = Label(m, image=img40, borderwidth=0)
    L_day5 = Label(m, image=img50, borderwidth=0)
    L_day6 = Label(m, image=img60, borderwidth=0)
    L_day7 = Label(m, image=img70, borderwidth=0)

    L_day1.grid(row=0, column=0, sticky='w')
    L_day2.grid(row=1, column=0, sticky='w')
    L_day3.grid(row=2, column=0, sticky='w')
    L_day4.grid(row=3, column=0, sticky='w')
    L_day5.grid(row=4, column=0, sticky='w')
    L_day6.grid(row=5, column=0, sticky='w')
    L_day7.grid(row=6, column=0, sticky='w')

    L_day1.image = img10
    L_day2.image = img20
    L_day3.image = img30
    L_day4.image = img40
    L_day5.image = img50
    L_day6.image = img60
    L_day7.image = img70

    taskimages = [img1, img2, img3, img4, img5, img6, img7]
    timeimages = [img01, img02, img03, img04, img05, img06, img07]

    timeedits = [edit01, edit02, edit03, edit04, edit05, edit06, edit07]
    taskedits = [edit1, edit2, edit3, edit4, edit5, edit6, edit7]

    # if datetime.datetime.now().time().hour < 23:
    last_scheduled_time = datetime.time(datetime.datetime.now().time().hour + 1, 0)
    # else:
    #     last_scheduled_time = datetime.datetime.today() + datetime.timedelta(days=1)
    day_count = 0
    for day in weekly_allocated_hrs:  # each day
        task_name = ""  # stores the names of the tasks
        if day_count > 0:
            last_scheduled_time = datetime.time(8, 0)
        y = 15
        tasks = weekly_allocated_hrs.get(day)
        day_index = days_of_the_week.index(day)
        for t_name, task_hrs in tasks.items():  # iterates through each task in task list for given day
            task_name = task_name + t_name + "\n"
            task_start_timestamp = str(last_scheduled_time.strftime("%H:%M"))
            # if last_scheduled_time.hour < (24 - task_hrs):
            task_end_time_hrs = last_scheduled_time.hour + task_hrs
            # else:
            #     task_end_time_hrs = last_scheduled_time.hour + task_hrs - 24
            timestamp_string = task_start_timestamp + " to " + str(task_end_time_hrs) + ":00" + "\n"
            last_scheduled_time = datetime.time(task_end_time_hrs)
            timeedits[day_index].text((60, y), timestamp_string, ('white'), font=textfont2)
            y += 15

        day_count += 1
        taskedits[day_index].text((80, 15), task_name, ('white'), font=textfont2)
        timeimages[day_index] = ImageTk.PhotoImage(timeimages[day_index])
        taskimages[day_index] = ImageTk.PhotoImage(taskimages[day_index])

        Task = Label(m, image=taskimages[day_index])

        Task.grid(row=day_index, column=2)
        Task.image = taskimages[day_index]

        Time = Label(m, image=timeimages[day_index])
        Time.grid(row=day_index, column=1)
        Time.image = timeimages[day_index]

def send_mail():
    s = smtplib.SMTP('smtp.gmail.com', 587)  # 587 is the connection port socket. Establishing window
    s.starttls()  # for security purposes
    sender_id = 'task1manager1@gmail.com'
    sender_password = '***'
    x = True  # conditional variable x
    while x:
        try:
            email = input('Enter email id to which you want a reminder to be sent:')  # receiver email
            s.login(sender_id, sender_password)
            message1 = 'Hello'
            message2 = 'This is a gentle reminder to complete your tasks as per schedule. Have a great day!\n'
            message_final = message1 + ' ' + email + ' ' + message2 + json.dumps(weekly_allocated_hrs, indent=4)
            s.sendmail(sender_id, email, message_final)
            print('Email reminder sent!')
            x = False
        except:
            print('Email could not be sent. Please enter a valid email')
    s.quit()


''' 
Generate next week depending on the day today - Ex: if today is Friday, table will have days from Friday to Thursday
'''
def generate_days_of_the_week_list():
    day_names = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]

    # days of the week are numbered 0-6 for Mon-Sun
    # get today's day of the week and use that to create a list of days for the next week
    day_num = datetime.datetime.today().weekday()
    index = day_num
    for i in range(7):
        if index + i >= 7:
            index = -1
        days_of_the_week.append(day_names[index + i])


def build_empty_weekly_allocation():
    for day in days_of_the_week:
        weekly_allocated_hrs[day] = {}
    #print(weekly_allocated_hrs)


if __name__ == '__main__':
    root = Tk()
    root.title("Task Scheduler")

    warning_label = Label(root, text='')
    warning_label.pack(side=BOTTOM, padx=10, pady=15)

    generate_days_of_the_week_list()
    build_empty_weekly_allocation()
    with open('./task_details.csv', 'w') as task_file:
        task_file.write(task_entry_labels[0] + ',' + task_entry_labels[1] + ',' + task_deadline_label + '\n')

        value_entry()
        root.mainloop()
        m = Tk()
        gen_button()
        send_mail()
