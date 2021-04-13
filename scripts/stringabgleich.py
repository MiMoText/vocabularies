
'''
Abgleich übersetzte DEL-Liste mit Begriffen aus der Annotation der Sekundärliteratur
'''

# == Imports == 

from os.path import join
import pandas as pd
import re

# == Files and folders ==
vocab_file = "DEL_übersetzt.csv"


def load_file(vocab_file):
    """
    Loads the vocabulary file from disk.
    Provides it as a pandas DataFrame.
    """
    with open(vocab_file, "r", encoding="utf8") as infile:
        vocabularies = pd.read_csv(infile, sep="\t")
        return vocabularies
    
def get_lists(vocabularies):
    """
    Provides terms as lists.
    """
    sek_list = []
    del_list = []
    
    for ind in vocabularies.index:
        if not pd.isnull(vocabularies['Seklit'][ind]):
            sek_list.append(vocabularies['Seklit'][ind])
        if not pd.isnull(vocabularies['DEL'][ind]):
            del_list.append(vocabularies['DEL'][ind])
    print("DEL-Begriffe:")
    print(del_list)
    print("Begriffe aus der Annotation der Sekundärliteratur:")
    print(sek_list)
    return sek_list, del_list


def make_dictionary(del_list):
    """
    Creates a dictionary with terms of DEL as keys and an empty list as values.
    """
    # Dictionary mit DEL-Begriffen als Keys und einer leeren Liste (für die alinierten Sek-begriffe) als Values
    del_dict = {}
    for item in del_list:
        del_dict[item] = ""   # leeren String anlegen
    return del_dict

def string_check(sek_list, del_list, del_dict):
    """
    Compares DEL terms with terms from secondary literature and tests for exact matches as well as matching substrings of 5 characters or more.
    Substrings which are part of affixes (word formation) are not considered.

    The matches found are written to the DEL terms into the dictionary.
    
    Unassigned terms from secondary literature are written in a list.
    """
    
    # list of substrings which are part of affixes (word formation)
    stop_list = ["isch", "ischen", "heit", "keit", "igkeit", "gkeit" , "gung", "igung", "rung", "erung", "hrung", "reich", "lich", "nisse", "der", "ität",
                 "ensch", "enscha", "enschaf", "enschaft", "nscha", "nschaf", "nschaft", "schaf", "schaft", "chaft", "stellung", "rinne",
                 'tellu', 'tellun', 'tellung', 'ellun', 'ellung', 'llung', 'nahme', 'tigke', 'tigkei', 'tigkeit', 'igkei', 'ligke', 'ligkei', 'ligkeit', 'ehung',
                 'tlich', 'lichk', 'lichke', 'lichkei', 'lichkeit', 'ichke', 'ichkei', 'ichkeit', 'chkei', 'chkeit', 'hkeit', ' der ', 'en de', 'en der', 'n der', 'andel',
                 'eiten', 'alitä', 'alität', 'lität', 'ental', 'entali', 'ntali', 'alitä', 'alität', 'lität', 'ische', 'ralis', 'liche', 'liche ', 'iche ', 'schafts',
                 'chafts', 'hafts', 'siere', 'nisie', 'nisier', 'isier', 'rtsch', 'gniss', 'gnisse', 'oliti', 'che M', ' Miss', 'tätig', 'tätigk', 'tätigke', 'tätigkei',
                 'tätigkeit', 'ätigk', 'ätigke', 'ätigkei', 'ätigkeit', 'rsche', 'rschei', 'rschein', 'schei', 'schein', 'chein','nunge', 'nungen', 'ungen',
                 'schaftl', 'schaftli', 'schaftlic', 'schaftlich', 'schaftliche', 'schaftliche ', 'chaftl', 'chaftli', 'chaftlic', 'chaftlich', 'chaftliche', 'chaftliche ',
                 'haftl', 'haftli', 'haftlic', 'haftlich', 'haftliche', 'haftliche ', 'aftli', 'aftlic', 'aftlich', 'aftliche', 'aftliche ', 'ftlic', 'ftlich', 'ftliche',
                 'ftliche ', 'tliche', 'tliche ', 'tigun', 'tigung', ' der W', 'der W', 'gemei', 'gemein', 'emein', 'ation', 'ersch', 'sche ', 'sche P', 'che P', 'misch', 'mische',
                 'mische ', 'ische ', 'sche ', 'onomi', ' des ','risch', 'erset', 'ersetz', 'ersetzu', 'ersetzun', 'ersetzung', 'rsetz', 'rsetzu', 'rsetzun', 'rsetzung', 'setzu',
                 'setzun', 'setzung', 'etzun', 'etzung', 'tzung', 'ierun', 'ierung', 'gesch', 'nität', 'isieru', 'isierun', 'isierung', 'sieru', 'sierun', 'sierung', 'ierun', 'ierung',
                 'emati', 'ematik', 'matik', ' von ', 'entum', 'tiani', 'tianis', 'ianis', 'nisch', 'nische', 'ratio', 'ration', 'alisi', 'alisie', 'alisier', 'lisie', 'lisier',
                 'alter','ismus', 'keits', 'schaftliche K', 'chaftliche K', 'haftliche K', 'aftliche K', 'ftliche K', 'tliche K', 'liche K', 'iche K', 'che K', 'ismus', 'ches ',
                 'chich', 'chicht', 'chichte', 'chichten', 'hicht', 'hichte', 'hichten', 'ichte', 'ichten', 'chten', 'liches', 'liches ', 'iches', 'iches ', 'ches ', 'alism', 'alismu',
                 'alismus', 'lismu', 'lismus', 'rische', 'rische ', 'lekti', 'ektiv', 'dheit', 'grati', 'gratio', 'gration', 'achtu', 'achtun', 'achtung', 'chtun', 'chtung', 'htung',
                 'enhei', 'enheit', 'nheit', 'ektiv', 'schen', 'iment', 'erisc', 'erisch', 'nlich', 'brauc', 'brauch', 'rauch']
    
    aligned_sek_terms = [] # list for terms from sek_list which are assigned to a DEL term
    single_sek_terms = []  # list for terms from sek_list which are not assigned to a DEL term
    
    for sek_term in sek_list:
        # extact match
        for del_term in del_list:
            if sek_term == del_term:  
                print(sek_term)
                
                aligned = del_dict[del_term]
                aligned_sek_terms.append(sek_term)
                if aligned == '':
                    aligned = sek_term
                    del_dict[del_term] = aligned
                else:
                    aligned = aligned + "; " + sek_term
                    del_dict[del_term] = aligned
            
            # one term is substring of the other
            elif sek_term in del_term or del_term in sek_term: 
                print(del_term + ", " + sek_term)
                
                aligned = del_dict[del_term]
                aligned_sek_terms.append(sek_term)
                if aligned == '':
                    aligned = sek_term
                    del_dict[del_term] = aligned
                else:
                    aligned = aligned + "; " + sek_term
                    del_dict[del_term] = aligned
            
            
            # common substrings
            else:
                substrings = []
                final = [sek_term[i:b+1] for i in range(len(sek_term)) for b in range(len(sek_term))]

                for i in final:
                    if i in sek_term and i in del_term and len(i) > 4:
                        if i not in stop_list:
                            substrings.append(i)
                            #print(substrings)
                if substrings:
                    print(del_term + ", " + sek_term)
                    aligned = del_dict[del_term]
                    aligned_sek_terms.append(sek_term)
                    if aligned == '':
                        aligned = sek_term
                    else:
                        aligned = aligned + "; " + sek_term
                    del_dict[del_term] = aligned
    
    # Getting the non-aligned terms from the secondary literature
    for sek_term in sek_list:
        if sek_term in aligned_sek_terms:
            pass
        else:
            single_sek_terms.append(sek_term)
            #print(sek_term)
    print("\n Dictionary mit DEL-Begriffen und zugeordneten Sekundärliteratur-Begriffen")
    print(del_dict)
    print("\n Nicht zugeordnete Begriffe aus der Annotation der Sekundärliteratur")
    print(single_sek_terms)
    return del_dict, single_sek_terms


def write_tsv(del_dict):
    df = pd.DataFrame.from_dict(del_dict, orient='index')
    df.to_csv("aligning.tsv", sep='\t', encoding="utf-8")
    
# == Coordinating function ==

def main(vocab_file):
    vocabularies = load_file(vocab_file)
    print("\n === Begriffe === \n ")
    sek_list, del_list = get_lists(vocabularies)
    del_dict = make_dictionary(del_list)
    print("\n === Gefundene Zuordnungen === \n ")
    del_dict, single_sek_terms = string_check(sek_list, del_list, del_dict)
    write_tsv(del_dict)
main(vocab_file)
