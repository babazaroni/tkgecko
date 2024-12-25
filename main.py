import sys
print("start print")
print(sys.executable)
print("end print")


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

from app.globals import timesheet_file

no_project_file = "No Project DB Loaded"
no_timesheet_file = "No Timesheet CSV Loaded"

def open_file_project():
    file_path = filedialog.askopenfilename(filetypes=[("Access DB","*.accdb")])
    if file_path:
        file_path_project.configure(text = file_path)
        project_extract(file_path)

def open_file_timesheet():
    file_path = filedialog.askopenfilename(filetypes=[("Csv","*.csv")])
    if file_path:
        file_path_timesheet.configure(text = file_path)
        glb.timesheet_df = read_csv(file_path)
        with open(file_path,"rb") as f:
            contents = f.read()
            f = BytesIO(contents)
            # glb.timesheet_df = read_csv(f,quoting=csv.QUOTE_NONE)
            glb.timesheet_df = read_csv(f)

def generate_report():
    content_report()
    create_report()
    report_status.configure(text = "report generated")

def generate_report_request():
    project_path = file_path_project.cget("text")
    if project_path == no_project_file:
        report_status.configure(text = "No Project DB specified",text_color="red")
        return
    if timesheet_file == no_timesheet_file:
        report_status.configure(text = "No Timesheet CSV specified",text_color = "red")
        return

    report_status.configure(text = "Preparing Report",text_color = "green")

    thread = threading.Thread(target = generate_report )
    thread.start()



ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("720x480")
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

app.mainloop()