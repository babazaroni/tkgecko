import sqlite3
import polars as pl

from app.mdb_parser import MDBParser, MDBTable

def get_df_info(db_path):
    db = MDBParser(file_path=db_path)

    table_list = [e for e in db.tables if not e.startswith('MS') and len(e) < 30]

    df_info = {}
    for table in table_list:
        df_info[table] = create_pl_df(db.get_table(table))

    return df_info


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

source_dir = "/home/cc/Solas/data/"
source_file = "Database_Updated_2024-6.accdb"

df_info = get_df_info(source_dir + source_file)

connection = sqlite3.connect("../newsql.db")
cursor = connection.cursor()

for table_name in df_info.keys():
    types = get_dtypes(df_info[table_name])
    columns = [f"[{name} {pl2sql_type(dtype)}]" for name,dtype in zip(df_info[table_name].columns,types)]

    field_list = ",".join(columns)
    sql = f"create table {table_name} ({field_list})"
    print(sql)

connection.close()
