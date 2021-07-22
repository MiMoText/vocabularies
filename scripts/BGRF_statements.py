'''
Extracts thematic statements from the BGRF, maps them to concepts and prepares statements for feeding into Wikibase.

Input:
- BGRF keywords (TSV)
- mapping file (TSV)
'''

# =======================
# Imports
# =======================

import mimotext_helpers as helpers
import numpy
import pandas as pd


# =======================
# Files and folders
# =======================

#bgrf_file = "BGRF_20.tsv"
bgrf_file = "BGRF_100.tsv"

bgrf_mapping = "themenkonzepte_bgrf.tsv"

resultfile = "bgrf100_about_statements.tsv"


# =======================
# Functions
# =======================

def get_keywords(mapping_matrix):
    '''
    - Takes mapping matrix.
    - Creates a list of lists of associated concept strings
      and their variants (keyword_lists).
    - Creates a dictionary with a mapping from each concept string
      to a thematic concept (mapping_dict).
    '''
    keyword_lists = []
    mapping_dict = {}
    for index, row in mapping_matrix.iterrows():
        list_of_keywords = [row['Konzept']]
        mapping_dict[row['Konzept']] = row['Themenwert']
        variants = (row['Varianten'])

        if variants != "n":
            variants = variants.split(";")
            for variant in variants:
                if variant == " ":   # case: cell entry ends with ;
                    pass
                else:
                    list_of_keywords.append(variant.strip())
                    mapping_dict[variant] = row['Themenwert']
        keyword_lists.append(list_of_keywords)

    return(keyword_lists, mapping_dict)
     

def extract_from_column(item, ind, counter, bgrf_matrix, rows, mapping_dict, column_name):
    '''
    For a specific keyword column from the BGRF matrix:
    mapping information is written into a dictionary.
    '''
    if item in bgrf_matrix[column_name][ind] and counter == 0:
        counter = counter + 1
        rows.append({'id' : ind, 'Spalte' : column_name, 'text' : bgrf_matrix[column_name][ind], 'Keyword': item, 'property': 'isabout', 'Themenwert': mapping_dict[item]})
        return rows, counter



def search_strings(bgrf_matrix, keywords_list, mapping_dict):
    '''
    Loop over rows of the BGRF matrix and search for concept strings.
    With extract_from_column() rows are created that are
    joined together to form a dataframe.
    '''
    rows = []
    for ind in bgrf_matrix.index:
        for k_list in keywords_list:  # check every concept string
            counter = 0
            for item in k_list:
                try:
                    rows, counter = extract_from_column(item, ind, counter, bgrf_matrix, rows, mapping_dict, 'r_c')
                except:
                    pass          
            
                try:
                    rows, counter = extract_from_column(item, ind, counter, bgrf_matrix, rows, mapping_dict, 'r_s')
                except:
                    pass
    
    df = pd.DataFrame(rows)
    
    return df
    

def delete_duplicates(df):
    '''
    Takes dataframe and deletes duplicates.
    
    Compares two consecutive entries with the same BGRF id.
    To do: id und Themenwert in einem Dictionary speichern,
    um auch Duplikate zu finden, die nicht direkt aufeinander folgen.
    
    '''
    ind_prev = ""
    ind_act = ""
    themenwert_act = ""
    themenwert_prev = ""
    for ind in df.index:
        ind_act = df["id"][ind]
        themenwert_act = df["Themenwert"][ind]
        
        if ind_act == ind_prev:
            # Compares current with previous concept
            if themenwert_act == themenwert_prev:
                print(ind_act, themenwert_act)
                df = df.drop(ind)
        ind_prev = ind_act
        themenwert_prev = themenwert_act
    return df


def save2tsv(df, resultfile):
    '''
    Saves dataframe to TSV.
    '''
    df = df.set_index('id')
    print(df.head())
    with open(resultfile, "w", encoding="utf8") as outfile: 
        df.to_csv(outfile, index_label ="id", sep="\t", line_terminator='\n')



# =======================
# Coordinating function
# =======================

def main(bgrf_file, bgrf_mapping, resultfile):
    bgrf_matrix = helpers.read_csv2(bgrf_file, "id")
    mapping_matrix = helpers.read_csv(bgrf_mapping)
    #print(bgrf_matrix)
    #print(mapping_matrix)
    keywords_list, mapping_dict = get_keywords(mapping_matrix)
    df = search_strings(bgrf_matrix, keywords_list, mapping_dict)
    delete_duplicates(df)
    df = delete_duplicates(df)
    save2tsv(df, resultfile)
    
main(bgrf_file, bgrf_mapping, resultfile)
    