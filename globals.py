#import pandas as pd
import polars as pl

PYODBC = True
ACCESS_PARSER = False
MDB_PARSER = False

db = None
app = None

project_file = " "
timesheet_file = " "

search_term = None
project_titles = None
project_titles_filtered = None
project_df = pl.DataFrame()
architects = None
architect_rates = None
#timesheet_df = pd.DataFrame()
#financial_df = pd.DataFrame()
timesheet_df = pl.DataFrame()
financial_df = pl.DataFrame()
tables_db = None
tables_list = None
table_selected = None
start_date = None
end_date = None
timesheet_dict= None
financials_dict = None
ref_iframe = None

dbgs_df = pl.DataFrame()

def global_clear():
    global table_selected,tables_list,timesheet_df,financial_df,project_file
    table_selected = None
    tables_list = None
    project_file = None
    ref_iframe = None
    timesheet_df = pl.DataFrame()
    financial_df = pl.DataFrame()

