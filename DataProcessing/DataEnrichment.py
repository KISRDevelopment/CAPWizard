import pandas as pd
import Utils.Helper as Helper


def enrich_df_with_template(df, tmpt_df, prefix=None):
    tmpt_df = tmpt_df.drop(['minp_level', 'minp_form'], axis=1)
    tech_code = f'{prefix + "_" if prefix else ""}tech_code'

    # Rename columns of tmpt_df to add prefix if provided
    if prefix:
        tmpt_df = tmpt_df.rename(columns={col: f"{prefix}_{col}" for col in tmpt_df.columns if col != 'tech_code'})

    # Apply the function to extract the base tech code
    df[f'clean_{tech_code}'] = df[tech_code].apply(Helper.extract_base_tech_code)
    # Perform a left join to keep all rows from df
    df = pd.merge(left=df, right=tmpt_df, left_on=f'clean_{tech_code}', right_on='tech_code', how='left')
    # Rename merged columns and remove the unnecessary columns
    df = df.drop([f'clean_{tech_code}'], axis=1)
    if tech_code == 'tech_code':
        df = df.rename({'tech_code_x': 'tech_code'}, axis=1)
        df = df.drop(['tech_code_y'], axis=1)
    else:
        df = df.drop(['tech_code'], axis=1)
    # Reorder DataFrame as necessary
    df = Helper.reorder_dataframe(df)
    return df


def enrich_with_template(tables_dict, tmpt_df):
    tables_dict = tables_dict.copy()

    for key in tables_dict:
        tables_dict[key] = enrich_df_with_template(tables_dict[key].copy(), tmpt_df)

    return tables_dict


def enrich_with_adb(adb_df, tables_dict):
    tables_dict = tables_dict.copy()
    adb_df = adb_df.copy()

    adb_df['adb_join_code'] = adb_df['level_code'].astype(str) + adb_df['form_code'].astype(str)
    for key in tables_dict:
        merged_df = pd.merge(
            tables_dict[key].astype({'tech_code': str, 'adb_join_code': str}),
            adb_df.astype({'tech_code': str, 'adb_join_code': str}),
            on=['tech_code', 'adb_join_code'],
            how='left'
        )
        merged_df = merged_df.drop(['adb_join_code', 'output_code'], axis=1)
        tables_dict[key] = Helper.reorder_dataframe(merged_df)

    return tables_dict


def enrich_with_ldr(tables_dict, ldr_df):
    tables_dict = tables_dict.copy()
    ldr_df = ldr_df.copy()

    ldr_df['extra_join_code'] = ldr_df['ts_code'].astype(str)
    for key in tables_dict:
        # Check if 'extra_join_code' column exists and all its values are NaN
        if 'extra_join_code' in tables_dict[key].columns and tables_dict[key]['extra_join_code'].isna().all():
            tables_dict[key] = tables_dict[key].drop(columns=['extra_join_code'])

        if 'extra_join_code' in list(tables_dict[key].columns):
            merged_df = pd.merge(
                tables_dict[key].astype({'extra_join_code': str}),
                ldr_df.astype({'extra_join_code': str}),
                on=['extra_join_code'],
                how='left'
            )
            merged_df = merged_df.drop(['extra_join_code'], axis=1)
            tables_dict[key] = Helper.reorder_dataframe(merged_df)

    return tables_dict


def embed_LDR_hour_and_type(tables_dict, slice_types):
    tables_dict = tables_dict.copy()
    slice_types = slice_types.iloc[:,0].tolist()
    num_types = len(slice_types)

    for key in tables_dict:
        tbl = tables_dict[key].copy()

        # for each tech_code in tbl, add an index column so that I have it numbered
        tbl['slice'] = (tbl.groupby(['tech_code', 'type']).cumcount() / num_types).astype(int)
        tbl['slice_time'] = (tbl['slice'] * 2).astype(str) + '-' + ((tbl['slice'] * 2) + 1).astype(str)

        # add another column goes from 0 to 2 and repeats until the last one
        tbl['slice_type'] = tbl.groupby(['tech_code', 'type']).cumcount() % num_types
        tbl['slice_type'] = tbl['slice_type'].apply(lambda x: slice_types[x])

        tables_dict[key] = Helper.reorder_dataframe(tbl)
    return tables_dict


def apply_demand_ldr_type_on_adb(adb_df, demand_codes):
    adb_df = adb_df.copy()

    # Step 1: Compute demand_code
    adb_df['demand_code'] = adb_df['form_code'] + '-' + adb_df['level_code']

    # Step 2: Find unique tech_codes where demand_code is in demand_codes
    tech_codes_to_update = adb_df[adb_df['demand_code'].isin(demand_codes)]['tech_code'].unique()

    # Step 3: Update ldr_type for those tech_codes
    adb_df.loc[adb_df['tech_code'].isin(tech_codes_to_update), 'ldr_type'] = 'demand'

    # Step 4: Drop demand_code column
    adb_df = adb_df.drop('demand_code', axis=1)
    
    return adb_df



def add_units_column(tables_dict):
    tables_dict = tables_dict.copy()
    units_dicts = {
        'Objective': 'USD',
        'Tech_in_out': 'MWyr',
        'Total_installed_cap': 'MW',
        'New_installed_cap': 'MW',
        'Investments_per_unit': 'USD/kW',
        'Investments_for_new_installations': 'kUSD',
        'Variable_cost_per_unit_of_output': 'USD/kWyr',
        'Variable_cost': 'kUSD',
        'Fixed_cost_per_unit_of_output': 'USD/kW/yr',
        'Fixed_cost': 'kUSD',
        'Tech_balance': 'MWyr',
        'Emissions': 'ktons',
        'LDR': 'MW',
    }
    for key in tables_dict:
        if key in units_dicts.keys():
            tables_dict[key]['units'] = units_dicts[key]
        elif 'szn' in key:
            tables_dict[key]['units'] = units_dicts['LDR']
    return tables_dict


# converts MWyr value column to Mtoe in a new column
def add_Mtoe_value(tables_dict, convert_all=False):
    tables_dict = tables_dict.copy()
    for key in tables_dict:
        if not convert_all:
            if '_LDR' not in key and key != 'Tech_in_out':
                continue
        tables_dict[key]['Mtoe'] = tables_dict[key]['value'] * 8760/(11.63*1e6)
    return tables_dict
