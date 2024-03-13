import pandas as pd
import numpy as np
import Utils.Helper as Helper


def clean_run_info(tbl_df):
    tbl_df = tbl_df.drop(tbl_df.index[:3])  # drop dummy rows
    # Drop the second row if it contains NaN values
    if tbl_df.iloc[1].isnull().any():
        tbl_df = tbl_df.drop(tbl_df.index[1])

    # Assign the first row to be the header
    header = tbl_df.iloc[0].copy()
    header.iloc[0] = 'tech_code'
    header.name = None
    tbl_df.columns = header.astype(str).map(lambda x: int(float(x)) if x.replace(".", "").isdigit() else x)
    tbl_df = tbl_df[1:].reset_index(drop=True)
    return tbl_df


def cast_numeric_cols(tbl_df):
    tbl_df.iloc[:,1:] = tbl_df.iloc[:,1:].astype(float)
    return tbl_df


def split_tech_code(tbl_df):
    col1 = tbl_df.columns[0]
    tbl_df.insert(1, 'adb_join_code', tbl_df[col1].str.split('___').str[1])
    tbl_df['adb_join_code'] = tbl_df['adb_join_code'].fillna('')
    tbl_df['extra_join_code'] = tbl_df['adb_join_code'].str.split('_').str.get(1)
    tbl_df['adb_join_code'] = tbl_df['adb_join_code'].str.split('_').str[0]
    tbl_df['adb_join_code'] = tbl_df['adb_join_code'].replace('', np.nan)
    tbl_df[col1] = tbl_df[col1].str.split('___').str[0]
    return tbl_df


def process_tables(tables_list):
    def get_title(tbl_df):
        return tbl_df.loc[1]['Unnamed: 2']

    tables_dict = {}
    for tbl in tables_list:
        title = get_title(tbl)
        tbl = clean_run_info(tbl)
        tbl = cast_numeric_cols(tbl)
        tbl = split_tech_code(tbl)
        tables_dict[title] = tbl
    return tables_dict


def handle_duplicate_year_specified_data(tables_dict):
    for key in tables_dict:
        if 'extra_join_code' not in list(tables_dict[key].columns):
            continue
        col = pd.to_numeric(tables_dict[key]['extra_join_code'], errors='coerce')
        if col.notna().all() and (col >= 1000).all() and (col <= 9999).all():
            new_rows_list = []
            df = tables_dict[key]
            prev_tech_code = None
            for _, r in df.iterrows():
                if prev_tech_code != r['tech_code']:
                    if prev_tech_code is not None:
                        new_rows_list.append(new_row)
                    prev_tech_code = r['tech_code']
                    new_row = {'tech_code': r['tech_code'], 'adb_join_code': r['adb_join_code']}
                new_row[int(r['extra_join_code'])] = r[int(r['extra_join_code'])]
            tables_dict[key] = pd.DataFrame(new_rows_list)
    return tables_dict


def handle_impexp(tables_dict):
    for key in tables_dict:
        # Sometimes its called _imp and exporting or _exp and importing
        # here I check when there is no input then it is import otherwise its export
        imp_exp_mask = tables_dict[key]['tech_activity'].isin(['import', 'export'])
        tables_dict[key].loc[imp_exp_mask, 'tech_activity'] = tables_dict[key].loc[imp_exp_mask, 'minp_code']\
                                                                .apply(lambda x: 'export' if pd.notna(x) and x != '' else 'import')

        # Make the output of an export as a negative value
        tact_mask = tables_dict[key]['tech_activity'] == 'export'
        ttype_mask = tables_dict[key]['type'] == 'main output'
        cols = tables_dict[key].columns[Helper.get_year_column_index(tables_dict[key]):]
        tables_dict[key].loc[tact_mask & ttype_mask, cols] *= -1

    return tables_dict


def interpolate_missing_years(df):
    def get_nearest_index(num, nums_list):
        for i in range(len(nums_list)):
            if num < nums_list[i]:
                return i - 1
        return -1
    df = df.copy()

    start_year_idx = Helper.get_year_column_index(df)
    start_year = df.columns[start_year_idx]  # Assuming the first year column is at index 5
    last_year = df.columns[-1]  # Assuming the last year column is the last column

    years = pd.Series(range(start_year, last_year + 1), dtype=int)

    missing_years = years[~years.isin(df.columns)]
    for year in missing_years:
        prev_year_idx = get_nearest_index(year, df.columns[start_year_idx:]) + start_year_idx
        prev_year = df.columns[prev_year_idx]
        next_year = df.columns[prev_year_idx + 1]
        df[prev_year] = pd.to_numeric(df[prev_year], errors='coerce')
        df[next_year] = pd.to_numeric(df[next_year], errors='coerce')
        interpolated_values = df[[prev_year, next_year]].interpolate(axis=1)
        df.insert(prev_year_idx+1, year, interpolated_values[prev_year] + (interpolated_values[next_year] - interpolated_values[prev_year]) * (
                    year - prev_year) / (next_year - prev_year))

    return df


def interpolate_for_tables(base_tables_dict):
    tables_dict = base_tables_dict.copy()
    for key in tables_dict:
        tables_dict[key] = tables_dict[key].copy()
        tables_dict[key] = interpolate_missing_years(base_tables_dict[key])
    return tables_dict


def transform_tables(df_dict):
    trf_df = {}
    
    for tbl in df_dict.keys():
        year_idx = Helper.get_year_column_index(df_dict[tbl])
        cols = df_dict[tbl].columns[:year_idx]

        if '_balance' in tbl:  # Skip the balance tables since they have different column structure
            trf_df[tbl] = df_dict[tbl]
        else:
            trf_df[tbl] = df_dict[tbl].melt(id_vars=cols, var_name="year", value_name="value")

    return trf_df
