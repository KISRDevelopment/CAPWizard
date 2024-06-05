import pandas as pd
import numpy as np


def extract_rows_between_markers(df, start_marker, end_marker, search_column=0):
    found_start = False
    extracted_rows = []

    for index, row in df.iterrows():
        if row[search_column] == start_marker:
            found_start = True
        elif row[search_column] == end_marker:
            if found_start:
                break
        elif found_start:
            extracted_rows.append(row)

    return pd.DataFrame(extracted_rows, columns=df.columns)


def extract_load_region(adb_df):
    adb_df = adb_df.copy()
    adb_df=extract_rows_between_markers(adb_df, start_marker='loadregions:', end_marker='energyforms:')
    adb_df = adb_df.dropna(how='all', axis=1)
    adb_df = adb_df.iloc[2:,1:-1]  # drop first two rows and first and last cols since they don't have any info
    mid_point = int(len(adb_df)/2)
    ldr_names=adb_df.iloc[:mid_point,:].reset_index(drop=True)
    ldr_length=adb_df.iloc[mid_point:,:].reset_index(drop=True)

    result = []
    for idx in ldr_names.index:
        for col in ldr_names.columns:
            if ldr_names.at[idx, col] == '\\' or pd.isna(ldr_names.at[idx, col]):
                continue
            result.append({
                'season': idx+1,
                'ts_code': ldr_names.at[idx, col],
                'ts_length': ldr_length.at[idx, col]
            })

    ldr_df = pd.DataFrame(result)
    ldr_df['season_code']=ldr_df['ts_code'].str[0]
    ldr_df['day_code']=ldr_df['ts_code'].str[1]
    ldr_df['time_code']=ldr_df['ts_code'].str[2]
    ldr_df['ts_length']=ldr_df.pop('ts_length')
    return ldr_df.reset_index(drop=True)


def extract_tech_load_curves(adb_df):
    adb_df = adb_df.copy()
    adb_df = extract_rows_between_markers(adb_df, start_marker='loadcurve:', end_marker='relationsc:')
    adb_df = adb_df.replace('\\', np.nan)
    adb_df = adb_df.dropna(axis=1, how='all')

    keys = []
    values = []
    for index, row in adb_df.iterrows():
        for col in adb_df.columns[1:]:
            keys.append(row[0])
            values.append(row[col])
    adb_df = pd.DataFrame({'key': keys, 'value': values})
    adb_df = adb_df[~adb_df['value'].isna()]
    adb_df['key'] = adb_df['key'].ffill()
    adb_df.insert(1, 'ldr_type', adb_df['key'].apply(lambda x: x.rsplit('.', 1)[-1] if '.' in x else np.nan))
    adb_df.insert(1, 'tech_code' , adb_df['key'].str.split('.', expand=True)[1].where(adb_df['key'].str.contains('.'), np.nan).replace({None: np.nan}))
    adb_df.reset_index(drop=True)
    return adb_df


def extract_demand_codes(adb_df):
    adb_df = adb_df.copy()
    adb_df = extract_rows_between_markers(adb_df, start_marker='demand:', end_marker='loadcurve:')

    codes = []
    for index, row in adb_df.iterrows():
            if row[0] not in codes:
                codes.append(row[0])
    return codes


def extract_adb_energy_forms(adb_df):
    adb_df = adb_df.copy()
    adb_df=extract_rows_between_markers(adb_df, start_marker='energyforms:', end_marker='demand:')
    adb_df = adb_df[(adb_df[0] != '#') & (adb_df[1] != '#')]
    adb_df=adb_df.dropna(axis=1, how='all')
    adb_df = adb_df.replace(['#', '*'], np.nan)
    adb_df=adb_df.dropna(axis=0, how='all')
    # adb_df = adb_df.iloc[:, :-1]  # drop last column
    # Create a new column for the level character
    adb_df[4] = adb_df.apply(lambda row: row[1] if pd.isna(row[2]) else np.nan, axis=1)
    # Forward fill the level name and character
    adb_df.iloc[:, 0].ffill(inplace=True)
    adb_df.iloc[:, -1].ffill(inplace=True)
    adb_df = adb_df[adb_df[2].notna()]  # Drop the level row (its going to have a NaN in column 2)
    adb_df[3] = adb_df[3].apply(lambda x: not pd.isna(x))
    adb_df.columns = ['level', 'form', 'form_code', 'hasldr', 'level_code']
    adb_df['fuel_code'] = adb_df['form_code'] + '-' + adb_df['level_code']  # Create the coding for the energy
    return adb_df.reset_index(drop=True)


def extract_tech_fyear(adb_df):
    adb_df = adb_df.copy()
    adb_df = extract_rows_between_markers(adb_df, start_marker='systems:', end_marker='resources:')
    adb_df = adb_df.replace(['#', '*'], np.nan)
    adb_df = adb_df.dropna(axis=1, how='all')
    # Filter the df to hold only the systems and their fyear
    adb_df = adb_df[(~adb_df[0].isna()) | adb_df[1].isin(['fyear'])]
    adb_df = adb_df.iloc[:, :3]  # keep only lookup info instead of actual value
    # fill the first column with the name and when its a mode of operation then take the name and put the mode of operation between []
    adb_df.iloc[:, 0].ffill(inplace=True)
    adb_df = adb_df[adb_df[1] == 'fyear']  # Keep only data related to fyear
    adb_df = adb_df[[0,2]]
    adb_df.columns = ['tech_code', 'fyear']
    return adb_df.copy()


def extract_adb_systems(adb_df):
    adb_df = adb_df.copy()
    adb_df=extract_rows_between_markers(adb_df, start_marker='systems:', end_marker='resources:')
    adb_df = adb_df.replace(['#', '*'], np.nan)
    # Filter the df to hold only the systems and their inputs and outputs
    adb_df = adb_df[(~adb_df[0].isna()) | adb_df[1].isin(['activity','minp','moutp','inp','outp'])]
    # Replace the activity with actual full name
    adb_df[1] = adb_df[1].replace({
        'minp': 'main input',
        'moutp': 'main output',
        'inp': 'input',
        'outp': 'output'
    })
    adb_df = adb_df.iloc[:, :3]  # keep only lookup info instead of actual value

    # fill the first column with the name and when its a mode of operation then take the name and put the mode of operation between []
    adb_df.iloc[:, 0].ffill(inplace=True)
    updated_values = []  # List to store updated values

    for idx, row in adb_df.iterrows():
        if pd.isna(row[0]):
            updated_value = latest_text
        elif isinstance(row[0], (int, float)):
            updated_value = f"{latest_text}[{str(row[0])[:-1]}]"
        else:
            latest_text = row[0]
            updated_value = row[0]
        updated_values.append(updated_value)

    # Update the DataFrame column with the new values
    adb_df.iloc[:, 0] = updated_values

    # Extract activity id
    for index, row in adb_df.iterrows():
        adb_df.loc[index] = row.ffill()
    adb_df[1] = adb_df.apply(lambda row: 'activity' if row[1] == row[2] else row[1], axis=1)
    adb_df['activity'] = np.where(adb_df[1] == 'activity', adb_df[2], np.nan)
    adb_df['activity'] = adb_df.groupby(0)['activity'].transform(lambda x: x.ffill())
    adb_df = adb_df.loc[~(adb_df[1] == 'activity')]

    adb_df.columns = ['tech_code', 'type', 'fuel_code', 'activity_code']
    return adb_df.reset_index(drop=True)


def insert_technology_code(adb_df):
    adb_df['mout_code'] = adb_df.apply(lambda row: row['form_code'] if row['type'] == 'main output' else np.NaN, axis=1)
    adb_df['mout_code'] = adb_df.groupby('tech_code')['mout_code'].ffill().bfill()
    adb_df['minp_code'] = adb_df.apply(lambda row: row['form_code'] if row['type'] == 'main input' else np.NaN, axis=1)
    adb_df['minp_code'] = adb_df.groupby('tech_code')['minp_code'].ffill()
    adb_df['minp_code'] = adb_df.groupby('tech_code')['minp_code'].bfill()
    adb_df['mout_lvl_code'] = adb_df.apply(lambda row: row['level_code'] if row['type'] == 'main output' else np.NaN, axis=1)
    adb_df['mout_lvl_code'] = adb_df.groupby('tech_code')['mout_lvl_code'].ffill().bfill()

    adb_df['full_code'] = adb_df['mout_lvl_code'].astype(str) +\
                            adb_df['minp_code'].fillna('.').astype(str) +\
                            adb_df['activity_code'].astype(str) +\
                            adb_df['mout_code'].astype(str)
    return adb_df


def extract_adb_time_steps(adb_df, nrun=None):
    adb_df = adb_df.copy()
    adb_df = extract_rows_between_markers(adb_df, start_marker='drate:', end_marker='loadregions:')
    adb_df = adb_df.drop([0,1], axis=1).dropna(axis=1).reset_index(drop=True).T.reset_index(drop=True)
    if nrun:
        return adb_df[:nrun+1]
    else:
        return adb_df

def extract_adb_plant_life(adb_df):
    cols = extract_adb_time_steps(adb_df)[0].tolist()
    adb_df = adb_df.copy()
    adb_df = extract_rows_between_markers(adb_df, start_marker='systems:', end_marker='resources:')
    adb_df = adb_df.replace(['#', '*'], np.nan)
    adb_df = adb_df[(~adb_df[0].isna()) | adb_df[1].isin(['pll'])].reset_index(drop=True)
    adb_df[1] = adb_df[1].apply(lambda x: x if x in ['pll'] else np.nan)
    adb_df[0] = adb_df.apply(lambda row: np.nan if ((not pd.isna(row[0])) and str(row[0]).isdigit()) else row[0], axis=1)
    adb_df[0].ffill(inplace=True)
    adb_df = adb_df.dropna(subset=[1])
    adb_df = adb_df.dropna(how='all', axis=1)
    adb_df = adb_df.reset_index(drop=True)
    adb_df = adb_df.ffill(axis=1)
    adb_df = adb_df.drop([1,2], axis=1)
    if len(adb_df.columns) < len(['tech_code'] + cols):
        diff = len(['tech_code'] + cols) - len(adb_df.columns)
        for i in range(diff):
            adb_df[str(i)] = np.nan
    adb_df = adb_df.ffill(axis=1)
    adb_df.columns = ['tech_code'] + cols
    adb_df = adb_df.melt(id_vars='tech_code', var_name='year', value_name='pll')
    adb_df['year'] = adb_df['year'].astype(int)
    return adb_df


def extract_adb_historical_capacity(adb_df):
    adb_df = adb_df.copy()
    adb_df = extract_rows_between_markers(adb_df, start_marker='systems:', end_marker='resources:')
    adb_df = adb_df.replace(['#', '*'], np.nan)
    adb_df = adb_df[(~adb_df[0].isna()) | adb_df[1].isin(['hisc'])].reset_index(drop=True)
    adb_df[1] = adb_df[1].apply(lambda x: x if x in ['hisc'] else np.nan)
    adb_df[0] = adb_df.apply(lambda row: np.nan if ((not pd.isna(row[0])) and str(row[0]).isdigit()) else row[0], axis=1)
    adb_df[0].ffill(inplace=True)
    adb_df = adb_df.dropna(subset=[1])
    adb_df = adb_df.drop([1,2,3], axis=1)
    adb_df = adb_df.dropna(how='all', axis=1)
    adb_df = adb_df.reset_index(drop=True).T.reset_index(drop=True).T

    new_rows = []
    for _, row in adb_df.iterrows():
        tech_code = str(row[0])
        for j in range(1, len(row), 2):
            if not pd.isna(row[j]):
                new_rows.append([tech_code, int(row[j]), row[j+1]])
    return pd.DataFrame(new_rows, columns=['tech_code', 'year', 'value'])


def extract_tables(result_df):
    def clean_it(df, start, end):
        cleaned_df = df.replace(r'^\s*$', np.nan, regex=True)
        cleaned_df = cleaned_df.iloc[start:end].dropna(how='all').reset_index(drop=True)
        return cleaned_df
    first_col = result_df.columns[0]
    mask = result_df[first_col].str.contains('Table', na=False)
    indices = result_df[mask].index.tolist()
    tables = []
    start_index = indices[0]
    for index in indices[1:]:
        tables.append(clean_it(result_df, start_index, index))
        start_index = index
    tables.append(clean_it(result_df, start_index, len(result_df)))
    return tables
