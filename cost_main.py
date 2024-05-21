import pandas as pd
import numpy as np 
from CostCalculator.CostCalculation import calculate_costs
import CostCalculator.TopologyConvertor as Convertor
import DataProcessing.DataEnrichment as Enricher
import Utils.DataIO as DataIO

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

    # Specify file paths
    results_file_path = 'Processed_results.xlsx'
    template_file_path = 'Template.xlsx'
    
    # Read Excel file
    tmpt_df = DataIO.read_template_file(template_file_path)
    result_df = pd.read_excel(results_file_path, sheet_name='Tech_in_out')
    V_df = pd.read_excel(results_file_path, sheet_name='Variable_cost')
    F_df = pd.read_excel(results_file_path, sheet_name='Fixed_cost')

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
        #     break
        # break

    df = Convertor.create_cost_dataframe(results)
    df = Enricher.enrich_df_with_template(df, tmpt_df, prefix='src')
    df = Enricher.enrich_df_with_template(df, tmpt_df,  prefix='dst')

    cols_to_move = ['total_cost_USD','units_MWyr']
    ordered_cols = [col for col in df.columns if col not in cols_to_move] + cols_to_move
    df = df[ordered_cols]

    df['USD_per_MWh'] = (df.total_cost_USD/df.units_MWyr)/8760
    df[['total_cost_USD', 'units_MWyr']] = df[['total_cost_USD', 'units_MWyr']].astype(float).round(3)
    df[['USD_per_MWh']] = df[['USD_per_MWh']].astype(float).round(8)
    df.to_csv('src_dst_costs.csv')
    df.drop('USD_per_MWh', axis=1, inplace=True)

    groupby_cols = [c for c in list(df.columns) if not (c.startswith('dst_') or c in ['total_cost_USD', 'units_MWyr'])]
    df1 = df.copy().groupby(groupby_cols, dropna=False)[['total_cost_USD', 'units_MWyr']].sum().reset_index()
    df1['USD_per_MWh'] = (df1.total_cost_USD/df1.units_MWyr)/8760
    df1[['total_cost_USD', 'units_MWyr']] = df1[['total_cost_USD', 'units_MWyr']].astype(float).round(3)
    df1[['USD_per_MWh']] = df1[['USD_per_MWh']].astype(float).round(8)
    df1.to_csv('src_costs.csv')

    groupby_cols = [c for c in list(df.columns) if not (c.startswith('src_') or c in ['total_cost_USD', 'units_MWyr'])]
    df2 = df.copy().groupby(groupby_cols, dropna=False)[['total_cost_USD', 'units_MWyr']].sum().reset_index()
    df2['USD_per_MWh'] = (df2.total_cost_USD/df2.units_MWyr)/8760
    df2[['total_cost_USD', 'units_MWyr']] = df2[['total_cost_USD', 'units_MWyr']].astype(float).round(3)
    df2[['USD_per_MWh']] = df2[['USD_per_MWh']].astype(float).round(8)
    df2.to_csv('dst_costs.csv')

    # print(df)

if __name__ == "__main__":
    main()
