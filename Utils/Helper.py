import pandas as pd
import re
import os


def get_year_column_index(df):
    for idx, col in enumerate(df.columns):
        if type(col) == int:
            return idx


def extract_base_tech_code(tech_code):
    """ Extracts the base tech code by removing suffixes like [2.0.], [3.0.], [2.], [3.], etc. """
    return re.sub(r'\[\d+(\.\d+)?\.\]', '', tech_code)


def reorder_dataframe(df):
    # Separate string columns and year columns
    string_cols = []
    year_cols = []
    
    for col in df.columns:
        if isinstance(col, int):
            year_cols.append(col)
        else:
            string_cols.append(col)
    
    # Sort year columns in ascending order
    year_cols.sort()

    # Reorder columns with string columns first, followed by sorted year columns
    reordered_cols = string_cols + year_cols
    
    # Create the reordered DataFrame
    reordered_df = df[reordered_cols]
    
    return reordered_df


def print_tables_dict(tables_dict):
    for key in tables_dict:
        print(key+'\n')
        print(tables_dict[key])
        print('\n============================================================================\n')


def combine_sheets(processed_sheets, new_sheet, sheet_name):
    for key in new_sheet:
        s = new_sheet[key].copy()
        s.insert(0, 'sheet', sheet_name)
        
        if key in processed_sheets:
            processed_sheets[key] = pd.concat([processed_sheets[key], s], ignore_index=True)
        else:
            processed_sheets[key] = s
            
    return processed_sheets


def get_desktop_path():
    if 'USERPROFILE' in os.environ:
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')  # Windows
    else:
        return os.path.join(os.path.expanduser('~'), 'Desktop')  # macOS or Linux
