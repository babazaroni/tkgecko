

#from google.cloud.storage.transfer_manager import PROCESS
import globals as glb
from excel import *
import datetime as dt
import pprint
from collections import defaultdict

from globals import ACCESS_PARSER, MDB_PARSER, PYODBC


class GeneralException(Exception):
    def __init__(self,message):
        super().__init__(message)
        self.message = message



def content_report(report_path):

    if glb.timesheet_df.is_empty() or glb.project_df.is_empty():
        print("not all files loaded")
        return

    process_time_sheet()
    process_financials()

    report_file_name = create_report(report_path)

    return report_file_name


def create_key(input):
    output = ''.join(e for e in input if e.isalnum())
    return output

def process_financials():

    project = None;phase = None;source = None

    glb.financials_dict = {}

    first_amount = None
    entries = None
    source_sum = 0

    print("process_financials:")
    pprint.pprint(glb.financial_df)

    for row in glb.financial_df.iter_rows(named = True):

        project_identifier = "{} / {}".format(row['Project ID'],row['Project Title'])
        project_identifier_key = create_key(project_identifier)

        project = glb.financials_dict.get(project_identifier_key,{}); glb.financials_dict[project_identifier_key] = project
        project['project_identifier'] = project_identifier

        tasks = project.get('tasks',{}); project['tasks'] = tasks

        task = tasks.get(row['Task'],{}); tasks[row['Task']] = task

        source = task.get(row['Source'],{'Sum':0}); task[row['Source']] = source

        entries = source.get('Entries',{}); source['Entries'] = entries
        amount = int(row['Amount'])
        entries[row['Description']] = {'Status':row['Status'],'Amount':amount}

        source['Sum'] += amount

    print("financials:")
    pprint.pprint(glb.financials_dict)



def process_time_sheet():

    glb.timesheet_dict = {}

    pprint.pprint("glb.timesheet_df:")
    pprint.pprint(glb.timesheet_df)

    for row in glb.timesheet_df.iter_rows(named=True):

        name = '{} {}'.format(row['fname'],row['lname'])
        local_date = dt.datetime.strptime(row['local_date'],'%Y-%m-%d')
        hours = float(row['hours'])
        jobcode1 = row['jobcode_1']
        jobcode2 = row['jobcode_2']
        phase = row['service item']

        jobcode2_key = create_key(jobcode2)

        project = glb.timesheet_dict.get(jobcode2_key,{}); glb.timesheet_dict[jobcode2_key] = project
        project['project_identifier'] = jobcode2

        tasks = project.get('tasks',{}); project['tasks'] = tasks

        task = tasks.get(row['service item'],{}); tasks[row['service item']] = task
        years = task.get('years',{}); task['years'] = years
        year = years.get(local_date.year,{}); years[local_date.year] = year
        name_totals = task.get('name_totals',{});task['name_totals'] = name_totals

        name_total = name_totals.get(name,0.0)
        rate = get_rate(name,local_date)
        if not rate:
            message = "No Rate for: {} at time {}".format(name,local_date)
            raise GeneralException(message)

        if glb.PYODBC:
            print("PYODBC rate",rate)
            rate = float(rate)

        if glb.ACCESS_PARSER:
            rate = float(rate[1:]) #access parser put $ in front
        if glb.MDB_PARSER:
            rate = float(rate) #Mdb parser does not

        year_hour_totals = year.get('hour_totals',{})
        t = year_hour_totals.get(name,[0.0,0.0])
        t[0] += hours
        t[1] += hours * rate
        year_hour_totals[name] = t

        name_total += hours * rate
        name_totals[name] = name_total

        task['name_sum'] = task.get('name_sum',0.0) + hours * rate

        year['hour_totals'] = year_hour_totals



    #print("book------------------------")
    #pprint.pp(glb.timesheet_dict)

    pass

def get_rate(name,date):
    """Get the hourly rate active at the date for person name"""

    rate = None

    for row in glb.architect_rates.iter_rows(named = True):
        an = glb.architects['Architects'][int(row['Architect'])-1]

        if PYODBC:
            start_date = row['Rate Start Date']
        if ACCESS_PARSER:
            start_date = dt.datetime.strptime(row['Rate Start Date'],"%Y-%m-%d 00:00:00")
        if MDB_PARSER:
            start_date = dt.datetime.strptime(row['Rate Start Date'],"%m/%d/%y 00:00:00")

        if name == an:
            if date>=start_date:
                rate = row['Hourly Rate']
    return rate

def create_summary(task,sheet,row,col):
    cv = Canvas()

    internal = task['Internal']
    i_entries = internal['Entries']

    yellow = "FFFF00"

    yellow_fill = PatternFill('solid', start_color=yellow)
    total_solas = 0

    for x,name in enumerate(i_entries.keys()):
        fill = None
        #if not x:
            #fill = yellow_fill
            #total_solas = i_entries[name]
            #cv.set(x, 2, name,fill = fill)
            #cv.set(x, 3, total_solas,fill=fill)

        cv.set(x,0,name,fill=fill)
        cv.set(x,1,i_entries[name]['Status'])
        cv.set(x,2,i_entries[name]['Amount'],fill = fill)

    external = task['External']
    e_entries = external['Entries']

    for x,name in enumerate(e_entries.keys()):
        cv.set(x,3,name)
        cv.set(x,4,e_entries[name]['Status'])
        cv.set(x,5,e_entries[name]['Amount'])

    bold_font = Font(bold=True)
    print('bold_font:',bold_font.bold)
    cv.set(cv.max_row+1,0,'Total Solas',font = bold_font)
    cv.set(cv.max_row,2,internal['Sum'],font =bold_font)
    cv.set(cv.max_row,3,'Total Project',font = bold_font)
    cv.set(cv.max_row,5,external['Sum'],font = bold_font)
    cv.set(cv.max_row+1,0,'',font = bold_font,fill = yellow_fill)
    cv.set(cv.max_row,1,'',font = bold_font,fill = yellow_fill)
    cv.set(cv.max_row,2,'',fill = yellow_fill)
    cv.set(cv.max_row,3,'Total Solas',font = bold_font,fill = yellow_fill)
    cv.set(cv.max_row, 4, '', fill=yellow_fill)
    cv.set(cv.max_row,5,total_solas,font = bold_font,fill = yellow_fill)

    cv.allocate()

    cell = Cell(border = Border(bottom = Side(border_style="thin"))) # dotted thin medium
    cv.all(cell)
    cv.border(Side(border_style="medium"))
    cv.set_row(cv.max_row,border = Border(top = Side(border_style="medium")))
    cv.set_col(2,border = Border(right = Side(border_style="medium")))

    cv.render(sheet,row,col)

def create_report(report_file_path):
    report_file_name = "report.xlsx"
    report_file_name = report_file_path

    #print(glb.project_titles_filtered)
    green1 = "006100"
    red = "FF0000"
    yellow = "FFFF00"

    green1_bold_font = Font(color = green1,bold=True)
    yellow_fill = PatternFill('solid', start_color=yellow)
    bold_font = Font(bold=True)

    workbook = Workbook()
    sheet = workbook.active

    row = 1

    if glb.timesheet_dict:

        for project in glb.timesheet_dict.keys():

            row_color(sheet, row, 'Z', red)

            row += 2

            summary_col = None

            tasks = glb.timesheet_dict[project]['tasks']

            for task in tasks.keys():
                print("create report project phase: ",project,task)

                cv1 = Canvas()

                project_identifier = glb.timesheet_dict[project]['project_identifier']
                cv1.set(0,0,"{} {}".format(project_identifier,task),font = green1_bold_font)

                names = get_names_from_groups(tasks[task])

                name_totals = tasks[task]['name_totals']

                for x,name in enumerate(names):
                    cv1.set(x+1,0,name)
                    cv1.set(x+1,3,name_totals[name])

                rate_sum = 0.0
                year_col = 0

                years = tasks[task]['years']

                for year in years.keys():
                    cv2 = Canvas()

                    cv2.set(0,0,'Sub Total')
                    cv2.set(0,1,'Rate')
                    cv2.set(0,2,year,fill = yellow_fill)

                    hour_totals = years[year]['hour_totals']

                    for x,name in enumerate(names):
                        sum = hour_totals.get(name, [0.0, 0.0])
                        cv2.set(x+1,0, sum[1] if sum[1] else "")
                        cv2.set(x+1,1, sum[1] / sum[0] if sum[1] and sum[0] else "")
                        cv2.set(x+1,2, sum[0] if sum[0] else "")

                    cv2.allocate()
                    cv2.all(Cell(border=Border(bottom=Side(border_style="thin"))))
                    cv2.border(Side(border_style="medium"))
                    cv2.render(sheet, row, year_col + 4)

                    year_col += 3

                try:
                    create_summary(glb.financials_dict[project]['tasks'][task], sheet, row,year_col + 5)
                except:
                    print("probably no financials specified")


                sum_row = len(names)+2
                cv1.set(sum_row,0,'Sub Total',)
                cv1.set(sum_row,3,tasks[task]['name_sum'],font = Font(bold=True))
                cv1.set(sum_row + 1,0,'Proposals')
                cv1.set(sum_row + 2,0,'Balance')

                cv1.allocate()
                cv1.render(sheet,row,0)

                row += cv1.max_row + 3



    sheet.column_dimensions['A'].width = 40
    print("workbook.save:")
    print(report_file_name)
    workbook.save(filename = report_file_name)
    #save_excel_to_html2(report_file_name,'report.html')

    return report_file_name


def get_names_from_groups(phase):
    names = []
    for year in phase['years'].keys():
        names.extend(phase['years'][year]['hour_totals'].keys())

    names = set(names)
    return list(names)


#import spire.xls as spire
#from spire.xls.common import *
def save_excel_to_html1(source,dest):
    workbook = spire.Workbook()
    workbook.LoadFromFile(source)
    sheet = workbook.Worksheets[0]

    options = spire.HTMLOptions()
    options.ImageEmbedded = True

    sheet.SaveToHtml(dest,options)

    return

#from xlsx2html import xlsx2html

def save_excel_to_html2(source,dest):
    #xlsx2html(source,dest)
    return



