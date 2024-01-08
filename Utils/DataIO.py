import pandas as pd
import numpy as np
import os


def read_file(file_path, sheet_name=None):
    if sheet_name is None:
        df = pd.read_excel(file_path, header=None)
    else:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df


def read_adb_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    data = []
    for line in lines:
        # Split the line into tokens
        tokens = line.strip().split()

        # Check if the line should start with NaN
        if line[0].isspace():
            tokens = [np.nan] + tokens

        # Convert tokens to numeric values, if possible
        row = [pd.to_numeric(token, errors='ignore') for token in tokens]
        data.append(row)

    # Find the length of the longest row
    max_length = max(len(row) for row in data)

    # Adjust all rows to have the same length, filling with NaN where data is missing
    data = [row + [np.nan] * (max_length - len(row)) for row in data]

    # Create a DataFrame from the adjusted data
    df = pd.DataFrame(data)

    return df


def read_template_file(filepath):
    tmpt_df = read_file(filepath, sheet_name='Data')
    tmpt_df = tmpt_df.rename(columns={'Tech display name': 'tech_name',
                                      'Tech MESSAGE name': 'tech_code',
                                      'Tech status': 'tech_status',
                                      'Tech activity': 'tech_activity',
                                      'Generation type': 'gen_type',
                                      'Forced main input level': 'minp_level',
                                      'Forced main input form': 'minp_form'
                                      })
    return tmpt_df


def export_dataframe_dict(filename, df_dict, output_dir=None, progress_callback=None):
    filepath = os.path.join(output_dir, filename+'.xlsx') if output_dir else filename+'.xlsx'

    with pd.ExcelWriter(filepath) as writer:
        for idx, key in enumerate(df_dict):
            msg = f'Exporting: {key} ~ {idx+1} of {len(df_dict)}'
            print(msg)
            if progress_callback:
                progress_callback(idx + 1, len(df_dict), msg)
            df_dict[key].to_excel(writer, sheet_name=key[:30], index=False)

        if progress_callback:
            progress_callback(1, 1, 'Closing Excel File...')

    print(f'File saved to {filepath}')
