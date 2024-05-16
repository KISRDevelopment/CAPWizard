import pandas as pd
import Utils.Helper as Helper


def enrich_with_template(tables_dict, tmpt_df):
    tables_dict = tables_dict.copy()
    columns_to_add = ['tech_activity', 'tech_status', 'tech_name']

    for key in tables_dict:
        # Enrich with network_db data
        for col in columns_to_add:
            lookup = dict(zip(tmpt_df['tech_code'], tmpt_df[col]))
            tables_dict[key] = tables_dict[key].copy()
            tables_dict[key].insert(1, col, tables_dict[key]['tech_code'])
            tables_dict[key][col] = tables_dict[key][col].apply(Helper.extract_base_tech_code)
            tables_dict[key].loc[:, col] = tables_dict[key][col].replace(lookup)

        # Enrich with gen_type
        insert_idx = tables_dict[key].columns.get_loc('tech_activity')
        gen_type_map = dict(zip(tmpt_df['tech_name'], tmpt_df['gen_type']))
        tables_dict[key].insert(insert_idx + 1, 'gen_type', tables_dict[key]['tech_name'].map(gen_type_map))

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
        tbl['slice'] = (tbl.groupby('tech_code').cumcount() / num_types).astype(int)
        tbl['slice_time'] = (tbl['slice'] * 2).astype(str) + '-' + ((tbl['slice'] * 2) + 1).astype(str)

        # add another column goes from 0 to 2 and repeats until the last one
        tbl['slice_type'] = tbl.groupby('tech_code').cumcount() % num_types
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
