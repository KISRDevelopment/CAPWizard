import pandas as pd
import numpy as np 
from CostCalculation import calculate_costs
import TopologyConvertor as Convertor

def main():

    # Crude oil, Electricity, HFO, NG, Diesel
    output_table = np.array([
        # oil extraction
        [6000,  0,  0,  0,  0],
        # oil import 
        [750,   0,  0,  0,  0],
        # refinery
        [0, 0, 2100, 1000, 500],
        # power plant
        [0, 1923+961.5+480.75+2884.5, 0, 0, 0],
        # import elec
        [0, 1000, 0, 0, 0],
        # final elec demand
        [0, 0, 0, 0, 0]
    ])

    # input table
    input_table = np.array([
        # oil extraction
        [0, 0, 0, 0, 0],

        # oil import 
        [0, 0, 0, 0, 0],

        # refinery
        [3750, 500, 0, 0, 0],

        # power plant 
        [3000, 0, 2100, 1000, 500],

        # import elec 
        [0, 0, 0, 0, 0],

        # final elec demand
        [0, 1923+961.5+480.75+2884.5-500, 0, 0, 0]
    ])
    V = np.array([100, 200, 300, 50, 400, 0])

    # Read Excel file
    result_df = pd.read_excel('./Processed_results.xlsx', sheet_name='Tech_in_out')
    V_df = pd.read_excel('./Processed_results.xlsx', sheet_name='Variable_cost')
    F_df = pd.read_excel('./Processed_results.xlsx', sheet_name='Fixed_cost')

    result_df['value'] = result_df['value'].abs()

    results = []
    for sc in result_df.sheet.unique():
        for yr in result_df.year.unique():
            print('---------------')
            print(' ', sc, '~', yr)
            print('---------------')
            temp_result = result_df[(result_df['sheet'] == sc) & (result_df['year'] == yr)].copy()
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
    df['USD_per_MWh'] = (df.total_cost_USD/df.units_MWyr)/8760
    df[['total_cost_USD', 'units_MWyr']] = df[['total_cost_USD', 'units_MWyr']].astype(float).round(3)
    df[['USD_per_MWh']] = df[['USD_per_MWh']].astype(float).round(8)
    df.to_csv('src_dst_costs.csv')
    df.drop('USD_per_MWh', axis=1, inplace=True)

    df1 = df.copy().groupby(['sheet', 'year', 'src_tech_code', 'src_activity_code', 'level', 'form'])[['total_cost_USD', 'units_MWyr']].sum().reset_index()
    df1['USD_per_MWh'] = (df1.total_cost_USD/df1.units_MWyr)/8760
    df1[['total_cost_USD', 'units_MWyr']] = df1[['total_cost_USD', 'units_MWyr']].astype(float).round(3)
    df1[['USD_per_MWh']] = df1[['USD_per_MWh']].astype(float).round(8)
    df1.to_csv('src_costs.csv')

    df2 = df.copy().groupby(['sheet', 'year', 'dst_tech_code', 'dst_activity_code', 'level', 'form'])[['total_cost_USD', 'units_MWyr']].sum().reset_index()
    df2['USD_per_MWh'] = (df2.total_cost_USD/df2.units_MWyr)/8760
    df2[['total_cost_USD', 'units_MWyr']] = df2[['total_cost_USD', 'units_MWyr']].astype(float).round(3)
    df2[['USD_per_MWh']] = df2[['USD_per_MWh']].astype(float).round(8)
    df2.to_csv('dst_costs.csv')

    # print(df)

if __name__ == "__main__":
    main()
