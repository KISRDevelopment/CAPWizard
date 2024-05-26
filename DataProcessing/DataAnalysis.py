import pandas as pd
import numpy as np
import Utils.Helper as Helper


def get_dummy_balance(df):
    df = df.copy()
    df = df[(df['tech_name'].str.lower() == 'dummy') & ((df['type'] == 'main output') | (df['type'] == 'output'))]
    return df


def is_dummy_active(dummy_balance):
    yr_idx = Helper.get_year_column_index(dummy_balance)
    dummy_balance = dummy_balance.copy().iloc[:,yr_idx:]
    return dummy_balance.values.sum() != 0


def check_balance_for_tables(tables_dict):
    if 'Tech_in_out' not in tables_dict.keys():
        return tables_dict
    tables_dict = tables_dict.copy()
    
    dummy_balance = get_dummy_balance(tables_dict['Tech_in_out'])
    if is_dummy_active(dummy_balance):
        print('\n************************************')
        print('* DUMMY SLACK VARIABLES ARE ACTIVE *')
        print('************************************\n')
    
    return tables_dict


def calc_tech_balance(tables_dict, sheet_name='Tech_balance'):
        if 'Tech_in_out' not in tables_dict.keys():
            return tables_dict
        df = tables_dict['Tech_in_out'].copy()

        inp_mask = df['type'].isin(['main input', 'input'])
        out_mask = df['type'].isin(['main output', 'output'])

        grouped_inp = df[inp_mask].groupby(['tech_code', 'activity_code'])
        grouped_out = df[out_mask].groupby(['tech_code', 'activity_code'])
        
        yr_cols = df.columns[Helper.get_year_column_index(df):]
        
        new_rows = []

        for (tech_code, activity_code), group in grouped_inp:
            total_input_row = {'tech_code': tech_code, 'activity_code': activity_code, 'type': 'total input'}
            total_output_row = {'tech_code': tech_code, 'activity_code': activity_code, 'type': 'total output'}
            diff_row = {'tech_code': tech_code, 'activity_code': activity_code, 'type': 'losses'}
            eff_row = {'tech_code': tech_code, 'activity_code': activity_code, 'type': 'efficiency'}
            
            for col in yr_cols:
                total_input_row[col] = group[col].sum()
                total_output_row[col] = grouped_out.get_group((tech_code, activity_code))[col].sum()
                diff_row[col] = round(abs(total_input_row[col]) - abs(total_output_row[col]), 4)
                eff_row[col] = round(total_output_row[col] / total_input_row[col], 4) if total_input_row[col] != 0 else 0

            new_rows.append(total_input_row)
            new_rows.append(total_output_row)
            new_rows.append(diff_row)
            new_rows.append(eff_row)

        # Special transformation for the resulting table
        new_df = pd.DataFrame(new_rows)
        year_idx = Helper.get_year_column_index(new_df)
        cols = new_df.columns[:year_idx]
        new_df = new_df.melt(id_vars=cols, var_name="year", value_name="value")
        new_df = new_df.pivot_table(index=['tech_code', 'activity_code', 'year'], columns='type', values='value').reset_index()
        new_df = new_df[['tech_code', 'activity_code', 'year', 'total input', 'total output', 'losses', 'efficiency']].copy()  # new col order

        tables_dict[sheet_name] = new_df

        return tables_dict


def annualize_inv_costs(df):
    df = df.copy()
    # There is a lag between installation of capacity and operation of the plant.
    # Therefore, it would be more representative to shift the investment cost by one period
    df['value'] = df.groupby(['tech_code'])['value'].shift().fillna(0)

    # Create a copy to avoid modifying the original dataframe during iteration
    result_df = df.copy()
    result_df['value'] = 0.0  # Reset all values to zero to start fresh

    # Loop over each unique 'tech_code'
    for _, sub_df in df.groupby(['tech_code']):
        # Loop through each row in the subgroup
        for idx, row in sub_df.iterrows():
            if row['value'] != 0:
                # Calculate the annualized value
                annual_value = row['value'] / row['pll']
                # Get the range of years to spread this value
                start_year = row['year']
                end_year = start_year + int(row['pll'])
                
                # Apply this value to all fully covered years
                full_years_mask = (result_df['tech_code'] == row['tech_code']) & \
                                  (result_df['year'] >= start_year) & (result_df['year'] < end_year)
                result_df.loc[full_years_mask, 'value'] += annual_value * result_df.loc[full_years_mask, 'period']
                # print(result_df[full_years_mask])

                # Handle fractional years at the end of the pll
                next_year = result_df[(result_df['tech_code'] == row['tech_code']) & 
                                      (result_df['year'] >= end_year)].min()['year']
                previous_year = result_df[(result_df['tech_code'] == row['tech_code']) & 
                                          (result_df['year'] < end_year)].max()['year']
                
                if pd.notna(next_year) and pd.notna(previous_year) and next_year != end_year:
                    # Apply fractional values
                    prev_mask = (result_df['tech_code'] == row['tech_code']) & (result_df['year'] == previous_year)
                    # next_mask = (result_df['tech_code'] == row['tech_code']) & (result_df['year'] == next_year)
                    # print(next_year, end_year, previous_year, start_year, annual_value)
                    result_df.loc[prev_mask, 'value'] -= annual_value * (next_year-end_year)
                    # result_df.loc[next_mask, 'value'] -= annual_value * (end_year-previous_year)

    
    result_df.drop(['pll','period'], axis=1, inplace=True)
    
    return result_df


#TODO: Make generalized
def handle_gas_network_own_use(df, yr_cols):
    for col in yr_cols:
        input_value = df.loc[(df['tech_code'] == 'KW_EN_GasNtwk_NG_tra') & (df['type'] == 'main input'), col].values
        output_value = df.loc[(df['tech_code'] == 'KW_EN_GasNtwk_NG_tra') & (df['type'] == 'main output'), col].values
        if input_value.size > 0 and output_value.size > 0:
            df.loc[(df['tech_code'] == 'KW_EN_GasNtwk_NG_tra') & (df['type'] == 'main input'), col] = input_value[0] - output_value[0]
    df.drop(df[(df['tech_code'] == 'KW_EN_GasNtwk_NG_tra') & (df['type'] == 'main output')].index, inplace=True)
    df.loc[df['tech_code'] == 'KW_EN_GasNtwk_NG_tra', ['type', 'level', 'form_code']] = ['diff', np.nan, np.nan]
    return df


#TODO: Make generalized
def apply_emission_factors(df, yr_cols):
    emission_factors = {
        'Natural_gas': 1769,
        'Crude_oil': 2312,
        'Gas_oil': 2337,
        'HFO': 2441,
        'LPG': 1980,
        'Others': 2337,
        'Pet_coke': 2700,
        'Ref_Gas': 1570
    }
    
    for form, factor in emission_factors.items():
        for col in yr_cols:
            df.loc[df['form'] == form, col] *= factor

    # Handle negative values for carbon capture
    for col in yr_cols:
        df.loc[df['tech_name'] == 'Simple CO2 capture in the entire energy system and storage', col] *= -1

    return df


#TODO: Make generalized
def calc_emissions(tables_dict, sheet_name='Emissions'):
    if 'Tech_in_out' not in tables_dict:
        return tables_dict

    df = tables_dict['Tech_in_out'].copy()
    yr_cols = df.columns[Helper.get_year_column_index(df):]
    
    df = handle_gas_network_own_use(df, yr_cols)
    
    filters = [
        (df['tech_code'] == 'KW_EN_GasNtwk_NG_tra'),
        (df['tech_code'] == 'KW_EN_Refinery_CO_pro') & (df['form_code'] == 'B'),
        (df['tech_name'] == 'Supply of fuels to power plants') & (df['type'] == 'main input'),
        (df['tech_name'] == 'Preparation of refinery fuel') & (df['type'] == 'main input') & (df['form'] != 'Heat_New'),
        (df['tech_name'] == 'Simple CO2 capture in the entire energy system and storage')
    ]
    df = df[pd.concat(filters, axis=1).any(axis=1)]
    drop_cols = ['hasldr','ldr_type','gen_type','main_input','season','ts_code','season_code','day_code','time_code','ts_length']
    df.drop(drop_cols, axis=1, inplace=True)

    df = apply_emission_factors(df, yr_cols).reset_index(drop=True)

    tables_dict[sheet_name] = df
    return tables_dict
