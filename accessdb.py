import globals as glb
import polars as pl
#import pandas as pd

from content_debug import add_debug

if glb.ACCESS_PARSER:
    # access_parser does not parse the big tables properly.  Misses entries
    from access_parser_c import AccessParser
if glb.MDB_PARSER:
    # mdb_parser uses mdb-tools, which mees a docker file is needed
    # Also does not parse dates into 4 digit years.  Better not have dates from 1900s
    from app.mdb_parser import MDBParser, MDBTable

if glb.PYODBC:
    import pyodbc as pyo
    pass

def project_extract(db_path):

    add_debug(("extract: " + db_path))

    #df = get_df_sql2()
    #print(df)

    #glb.tables_db = [e for e in glb.db.catalog.keys() if not e.startswith('MS') and len(e) < 30]
    #print("glb.tables_db:",glb.tables_db)
    #glb.table_selected = glb.tables_db[0]

    if glb.PYODBC:
        print("starting PYODBC")
        dbq_string = "DBQ={}".format(db_path)
        driver_string = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
        cnn_string = driver_string + dbq_string
        print("accessdb:", cnn_string)
        cnn = pyo.connect(cnn_string)
        cursor = cnn.cursor()
        glb.tables_list = [t.table_name for t in cursor.tables()]

        glb.project_df = create_df_sql("select * from [Project Data]",cnn)
        glb.architects = create_df_sql("select * from [Solas Architects]",cnn)
        glb.architect_rates = create_df_sql("select * from [Solas Architect Rates]",cnn).sort('Rate Start Date')
        glb.financial_df = create_df_sql("select * from [Financials]",cnn)

        glb.project_titles = glb.project_df['Project Title'].to_list()


    if glb.ACCESS_PARSER:
        print("starting ACCESS_PARSER")
        glb.db = AccessParser(db_path)
        glb.tables_list = [e for e in glb.db.catalog.keys() if not e.startswith('MS') and len(e) < 30]
        print("glb.tables_list:",glb.tables_list)
        table = glb.db.parse_table("Project Data")
        glb.project_df = pl.DataFrame(table)
        #glb.project_df = pd.DataFrame.from_dict(table)
        glb.project_titles = table['Project Title']
        architects = glb.db.parse_table('Solas Architects')
        glb.architects = pl.DataFrame(architects)
        architect_rates = glb.db.parse_table('Solas Architect Rates')
        #glb.architect_rates = pd.DataFrame.from_dict(architect_rates).sort_values(by=['Rate Start Date']).dropna(axis=0)
        glb.architect_rates = pl.DataFrame(architect_rates)
        financials = glb.db.parse_table('Financials')
        glb.financial_df = pl.DataFrame(financials)


    if glb.MDB_PARSER:
        print("starting MDB_PARSER")
        glb.db = MDBParser(file_path=db_path)
        glb.tables_list = [e for e in glb.db.tables if not e.startswith('MS') and len(e) < 30]
        glb.table_selected = glb.tables_list[0]

        table = glb.db.get_table("Project Data")
        print("table: Project Data")
        print(table)
        rows = [row for row in table]
        #glb.project_df = pd.DataFrame(rows,columns=table.columns)
        #glb.project_df = pd.DataFrame(rows,columns=table.columns)
        glb.project_df = pl.DataFrame(data = rows,orient = 'row',schema=table.columns)
        glb.project_titles = glb.project_df['Project Title'].to_list()
        table = glb.db.get_table("Solas Architects")
        glb.architects = create_df(table)
        table = glb.db.get_table("Solas Architect Rates")
        glb.architect_rates = create_df(table).sort('Rate Start Date')
        table = glb.db.get_table("Financials")
        glb.financial_df = create_df(table)

        print("glb.financial_df:", len(glb.financial_df))
        print("keys:",glb.financial_df.columns)

    glb.project_titles.sort()

def create_df_sql(sql,conn):
    cursor = conn.cursor()
    cursor.execute(sql)
    rows_tuples = cursor.fetchall()
    rows = [list(t) for t in rows_tuples]

    columns = [column[0] for column in cursor.description]


    df = pl.DataFrame(rows,schema=columns,orient='row')
    return df

def create_df(table):
    #print("create_df:",type(table))
    rows = [row for row in table]
    #df=pd.DataFrame(rows,columns=table.columns)
    df=pl.DataFrame(data = rows,orient = 'row',schema=table.columns)
    return df






