import sys
import os
import platform
from pathlib import Path
print("start print")
print(sys.executable)
print("end print")

#report_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + r"\report.xslx"
#report_path = "report.xslx"


if platform.system() == 'Windows':
    slash = "\\"
else:
    slash = "/"

report_path = str(Path.home())
report_path = report_path + slash + "report.xlsx"
print("report_path: ",report_path)

#sys.path.append('/home/cc/Solas/webapp/pythonProject/app')
from tkinter import filedialog
import customtkinter as ctk
import threading
from io import BytesIO
import time

import globals as glb
from content_report import create_report,content_report
from polars import read_csv
from accessdb import project_extract

no_project_file = "No Project DB Loaded"
no_timesheet_file = "No Timesheet CSV Loaded"

DEV = True

if DEV is True:
    project_file_dev_path = "/home/cc/Solas/Database Updated 2024-6.accdb"
    timesheet_file_dev_path = "/home/cc/Solas/data/timesheet_report_2024-01-01_thru_2024-09-27.csv"
else:
    project_file_dev_path = no_project_file
    timesheet_file_dev_path = no_timesheet_file



def open_file_project():
    file_path = filedialog.askopenfilename(filetypes=[("Access DB","*.accdb")])
    if file_path:
        file_path_project.configure(text = file_path)
        glb.project_file = file_path
        project_extract(file_path)

def open_file_timesheet():
    file_path = filedialog.askopenfilename(filetypes=[("Csv","*.csv")])
    if file_path:
        file_path_timesheet.configure(text = file_path)
        glb.timesheet_file = file_path
        glb.timesheet_df = read_csv(file_path)
        with open(file_path,"rb") as f:
            contents = f.read()
            f = BytesIO(contents)
            # glb.timesheet_df = read_csv(f,quoting=csv.QUOTE_NONE)
            glb.timesheet_df = read_csv(f)

def connect_timesheet():
    pass

def generate_report():
    content_report(report_path)
    report_status.configure(text = "report generated",text_color="green")

def generate_report_request():
    if file_path_project.cget("text") == no_project_file:
        report_status.configure(text = "No Project DB specified",text_color="red")
        return
    if file_path_timesheet.cget("text") == no_timesheet_file:
        report_status.configure(text = "No Timesheet CSV specified",text_color = "red")
        return

    generate_report()

def view_report_request():

    try:
        view_status.configure(text = "Viewing: " + report_path,text_color="green")
        print("view request")

        #file_path = os.getcwd() + "\\report.xslx"
        #file_path = r"C:\Users\babaz\OneDrive\Documents\GitHub\tkgecko\report.xslx"
        #file_path = "report.xlsx"

        if platform.system() == 'Windows':
            os.startfile(report_path)
        else:
            os.system("libreoffice {}".format(report_path))

        print(sys.executable)
        print(os.getcwd())
        #print(file_path)
        #desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        #print("desktop:",desktop)
    except Exception as e:
        view_status.configure(text = "Unable to view: " + report_path,text_color="red")
        print(e)
        pass

DEF_Y = 10

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("720x400")
app.title("Report Generator")

button_project = ctk.CTkButton(app,text = "Open Project DB",command = open_file_project)
button_project.pack(pady=DEF_Y)

file_path_project = ctk.CTkLabel(app,text= project_file_dev_path if DEV else no_project_file)
file_path_project.pack(pady=DEF_Y)

button_timesheet = ctk.CTkButton(app,text = "Open Timesheet",command = open_file_timesheet)
button_timesheet.pack(pady=2)

button_timesheet_connect = ctk.CTkButton(app,text = "Connect Timesheet",command = connect_timesheet)
button_timesheet_connect.pack(pady=2)

file_path_timesheet = ctk.CTkLabel(app,text=timesheet_file_dev_path if DEV else no_timesheet_file)
file_path_timesheet.pack(pady=DEF_Y)

button_report = ctk.CTkButton(app,text = "Generate Report",command = generate_report_request)
button_report.pack(pady=DEF_Y)

report_status = ctk.CTkLabel(app,text="")
report_status.pack(pady=DEF_Y)

button_view_report = ctk.CTkButton(app,text = "View Report",command = view_report_request)
button_view_report.pack(pady=DEF_Y)

view_status = ctk.CTkLabel(app,text="")
view_status.pack(pady=DEF_Y)

app.mainloop()