
import polars as pl
import numpy as np

df = pl.read_excel("data/Paycodes Standard.xlsx", sheet_name="Lønartskatalog")

df = df.select(["Navn", "Lønartnr", "Udskrivnings sekvens", "Type"])

df.write_csv("data/paycodes.csv")