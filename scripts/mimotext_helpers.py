import pandas as pd
import re

def read_csv(csv_file):
    '''
    Liest CSV ein und gibt sie als pandas dataframe zurück.
    '''
    with open(csv_file, "r", encoding="utf8") as infile:
        matrix = pd.read_csv(infile, sep="\t")
        return matrix

def read_csv2(csv_file, index_col_name):
    '''
    Liest CSV ein und gibt sie als pandas dataframe zurück.
    Nimmt zusätzlich Argument für die Index-Spalte
    '''
    with open(csv_file, "r", encoding="utf8") as infile:
        matrix = pd.read_csv(infile, sep="\t", index_col = index_col_name)
        return matrix
