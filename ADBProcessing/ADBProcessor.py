import pandas as pd
import numpy as np
import Utils.Helper as Helper


def transpose_main_input_column(adb_df):
    adb_df = adb_df.copy()
    main_input_dict = {}
    
    for _, row in adb_df.iterrows():
        if row['type'] == 'main input':
            main_input_dict[row['tech_code']] = row['form']

    adb_df.insert(1, 'main_input', adb_df['tech_code'].map(main_input_dict))

    return adb_df.reset_index(drop=True)


def insert_main_input_when_missing(adb_df, tmpt_df):
    # Create dictionaries for quick lookup
    level_dict = tmpt_df.set_index('tech_code')['minp_level'].to_dict()
    form_dict = tmpt_df.set_index('tech_code')['minp_form'].to_dict()
        
    tech_codes_missing_input = adb_df.groupby('tech_code')['type'].apply(lambda x: 'main input' not in x.values)
    tech_codes_missing_input = tech_codes_missing_input[tech_codes_missing_input].index

    new_rows = []
    for tech_code in tech_codes_missing_input:
        base_tech_code = Helper.extract_base_tech_code(tech_code)
        new_rows.append({'tech_code': tech_code,
                         'type': 'main input',
                         'level': base_tech_code,
                         'form': base_tech_code,
                         'code': np.nan})

    new_rows_df = pd.DataFrame(new_rows)

    # Using lookup_df for dynamic replacement
    new_rows_df['level'] = new_rows_df['level'].replace(level_dict)
    new_rows_df['form'] = new_rows_df['form'].replace(form_dict)

    adb_df = pd.concat([adb_df, new_rows_df], ignore_index=True)
    
    return adb_df.reset_index(drop=True)


def process_adb(adb_df, tmpt_df):
    adb_df = insert_main_input_when_missing(adb_df, tmpt_df)
    adb_df = transpose_main_input_column(adb_df)
    adb_df['output_code'] = adb_df.pop('code')
    return adb_df
