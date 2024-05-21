import numpy as np 
from CostCalculator.CostCalculation import calculate_costs
import CostCalculator.TopologyConvertor as Convertor

def embed_costs(tables_dict, progress_callback=None):
    result_df = tables_dict['Tech_in_out'].copy()
    V_df = tables_dict['Variable_cost'].copy()
    F_df = tables_dict['Fixed_cost'].copy()

    result_df['value'] = result_df['value'].abs()

    results = []
    total_combinations = len(result_df.sheet.unique()) * len(result_df.year.unique())
    processed_combinations = 0

    for sc in result_df.sheet.unique():
        for yr in result_df.year.unique():
            processed_combinations += 1
            progress_callback(processed_combinations, total_combinations, sc, yr)
            print('---------------')
            print(' ', sc, '~', yr)
            print('---------------')
            temp_result = result_df[(result_df['sheet'] == sc) & (result_df['year'] == yr)].copy()
            for col in temp_result.columns:
                if temp_result[col].dtype != 'float64':
                    temp_result[col].fillna('', inplace=True)

            # Filter V_df and F_df and then convert to numpy array
            temp_V_df = V_df[(V_df['sheet'] == sc) & (V_df['year'] == yr)]
            temp_V = temp_V_df.value.to_numpy()
            temp_F_df = F_df[(F_df['sheet'] == sc) & (F_df['year'] == yr)]
            temp_F = temp_F_df.value.to_numpy()

            input_table, output_table, tech_to_idx, fuel_to_idx = Convertor.create_inp_out(temp_result)

            # To add the cost for the artificial resource & demand nodes (the assigned costs are ignored in calculation)
            len_padding = len(tech_to_idx) - len(temp_V)
            temp_V = np.pad(temp_V, (0, len_padding))

            len_padding = len(tech_to_idx) - len(temp_F)
            temp_F = np.pad(temp_F, (0, len_padding))

            As_normed, As = Convertor.to_network(input_table, output_table)

            results.extend(calculate_costs(As_normed, As, temp_V, temp_F, tech_to_idx, fuel_to_idx, sc, yr))

    df = Convertor.create_cost_dataframe(results)
    df['per_unit_USD_per_MWh'] = (df.total_cost_USD/df.units_MWyr)/8760
    df[['total_cost_USD', 'units_MWyr']] = df[['total_cost_USD', 'units_MWyr']].astype(float).round(3)
    df[['per_unit_USD_per_MWh']] = df[['per_unit_USD_per_MWh']].astype(float).round(8)
    tables_dict['src_dst_costs'] = df.copy()
    df.drop('per_unit_USD_per_MWh', axis=1, inplace=True)

    df1 = df.copy().groupby(['sheet', 'year', 'src_tech_code', 'src_activity_code', 'level', 'form'])[['total_cost_USD', 'units_MWyr']].sum().reset_index()
    df1['per_unit_USD_per_MWh'] = (df1.total_cost_USD/df1.units_MWyr)/8760
    df1[['total_cost_USD', 'units_MWyr']] = df1[['total_cost_USD', 'units_MWyr']].astype(float).round(3)
    df1[['per_unit_USD_per_MWh']] = df1[['per_unit_USD_per_MWh']].astype(float).round(8)
    tables_dict['src_costs'] = df1

    df2 = df.copy().groupby(['sheet', 'year', 'dst_tech_code', 'dst_activity_code', 'level', 'form'])[['total_cost_USD', 'units_MWyr']].sum().reset_index()
    df2['per_unit_USD_per_MWh'] = (df2.total_cost_USD/df2.units_MWyr)/8760
    df2[['total_cost_USD', 'units_MWyr']] = df2[['total_cost_USD', 'units_MWyr']].astype(float).round(3)
    df2[['per_unit_USD_per_MWh']] = df2[['per_unit_USD_per_MWh']].astype(float).round(8)
    tables_dict['dst_costs'] = df2

    return tables_dict
