
import polars as pl

import app.globals as glb

from app.utils import table_from_df

def content_debug():
    table = table_from_df(glb.dbgs_df,"debug_table")
    return table

def add_debug(message):
    row = pl.DataFrame(
        {"Message":message}
    )

    glb.dbgs_df = glb.dbgs_df.vstack(row)