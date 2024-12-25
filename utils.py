from fasthtml.common import *

def table_from_df(df,id):

    if df.is_empty():
        table = Table(
            cls='table',
            id=id
        )
        return table

    table = Table(
        Thead(
            Tr(
                #*[Th(header) for header in df.columns.tolist()]
                *[Th(header) for header in df.columns],
            )
        ),
        Tbody(*[Tr(*[Td(d) for d in row]) for row in df.iter_rows()]),
        cls='table',
        id = id
    )
    return table
