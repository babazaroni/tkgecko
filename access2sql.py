import sqlite3
import polars as pl
import pandas as pd

import pyodbc as pyo
import sqlalchemy as sa

def get_source_cnn(db_path):
    dbq_string = "DBQ={}".format(db_path)
    driver_string = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
    cnn_string = driver_string + dbq_string
    print(cnn_string)
    #cnn = sa.create_engine(cnn_string)
    cnn = pyo.connect(cnn_string)
    return cnn

def get_data_types(cursor):
    return []

def get_df_info(db_path):
    db = MDBParser(file_path=db_path)

    table_list = [e for e in db.tables if not e.startswith('MS') and len(e) < 30]

    df_info = {}
    for table in table_list:
        df_info[table] = create_pl_df(db.get_table(table))

    return df_info

def create_pd_df_sql(sql,conn):
    df = pd.read_sql(sql,conn)
    return df
def create_pd_df_sql2(table,conn):
    df = pd.read_sql_table(table,conn)
    return df


def create_pl_df_sql(sql,conn):
    cursor = conn.cursor()
    cursor.execute(sql)
    rows_tuples = cursor.fetchall()
    rows = [list(t) for t in rows_tuples]

    columns = [column[0] for column in cursor.description]


    df = pl.DataFrame(rows,schema=columns,orient='row')
    return df


def create_pl_df(table):
    #print("create_df:",type(table))
    rows = [row for row in table]
    #df=pd.DataFrame(rows,columns=table.columns)
    df=pl.DataFrame(data = rows,orient = 'row',schema=table.columns)
    return df

def pl2sql_type(dtype):
    return dtype

def get_types(df):
    return []

def sql_type(df_type):
    if df_type=="object":
        return "TEXT"
    if df_type=="int64":
        return "INTEGER"
    if df_type=="float64":
        return "FLOAT"
    if df_type=="datetime64[ns]":
        return "DATETIME"
    if df_type=="bool":
        return "BOOLEAN"

    print("fatal error: no type for ",df_type)
    5/0

def get_sql_field_names(df):
    field_list =  [f"[{column}]" + " " +sql_type(df[column].dtype) for column in df.columns]
    return ",".join(field_list)

#source_dir = "/home/cc/Solas/data/"
#source_file = "Database_Updated_2024-6.accdb"

source_dir = "C:/Users/babaz/OneDrive/Desktop/Solas V1/"
source_file = "Database Updated 2024-V1.accdb"

source_cnn = get_source_cnn(source_dir + source_file)
source_cursor = source_cnn.cursor()

tables_list = [t.table_name for t in source_cursor.tables(tableType='TABLE')]

print("table_list:",tables_list)

dest_connection = sqlite3.connect("sql_new")
dest_cursor = dest_connection.cursor()



for table_name in tables_list:
    project_df = create_pd_df_sql(f"select * from [{table_name}]", source_cnn)
    #project_df = create_pd_df_sql2(table_name, source_cnn)

    sql_field_names = get_sql_field_names(project_df)

    exec_string = f"create table [{table_name}] ({sql_field_names})"

    dest_cursor.execute(exec_string)

    print(exec_string)
    print("table_name:",table_name)
    #print(project_df.dtypes)
    #print(sql_field_names)



    #columns = [f"[{name} {pl2sql_type(dtype)}]" for name,dtype in zip(df_info[table_name].columns,types)]

    #field_list = ",".join(columns)
    #sql = f"create table {table_name} ({field_list})"
    #print(sql)

dest_connection.close()
source_cnn.close()
