import sys
import os
from pathlib import Path
print("start print")
print(sys.executable)
print("end print")

#report_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + r"\report.xslx"
#report_path = "report.xslx"

report_path = str(Path.home())
report_path = report_path + r"\report.xlsx"
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
        #os.system("start excel.exe {}".format(report_path))
        #file_path = os.getcwd() + "\\report.xslx"
        #file_path = r"C:\Users\babaz\OneDrive\Documents\GitHub\tkgecko\report.xslx"
        #file_path = "report.xlsx"
        os.startfile(report_path)

        print(sys.executable)
        print(os.getcwd())
        #print(file_path)
        #desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        #print("desktop:",desktop)
    except:
        view_status.configure(text = "Unable to view: " + report_path,text_color="red")
        pass


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("720x600")
app.title("Report Generator")

button_project = ctk.CTkButton(app,text = "Open Project DB",command = open_file_project)
button_project.pack(pady=20)

file_path_project = ctk.CTkLabel(app,text=no_project_file)
file_path_project.pack(pady=20)

button_timesheet = ctk.CTkButton(app,text = "Open Timesheet",command = open_file_timesheet)
button_timesheet.pack(pady=20)

file_path_timesheet = ctk.CTkLabel(app,text=no_timesheet_file)
file_path_timesheet.pack(pady=20)

button_report = ctk.CTkButton(app,text = "Generate Report",command = generate_report_request)
button_report.pack(pady=20)

report_status = ctk.CTkLabel(app,text="")
report_status.pack(pady=20)

button_view_report = ctk.CTkButton(app,text = "View Report",command = view_report_request)
button_view_report.pack(pady=20)

view_status = ctk.CTkLabel(app,text="")
view_status.pack(pady=20)

app.mainloop()