import pandas as pd
import numpy as np


def generate_cap_table(title, units, adb_df, only_output, exclude_secondary_op_modes, eqn_func, precision=4):
     cap = f'title: {title}\nunit: {units}, 1.\ndirection: hor\npostdigits: {precision}\n@\n'
     adb_df = adb_df.copy()
     if only_output:
          adb_df = adb_df[adb_df['type'] == 'main output']
     if exclude_secondary_op_modes:
          adb_df['tech_code'] = adb_df['tech_code'].str.replace(r'\[\d+\.\]', '', regex=True)
          adb_df = adb_df[['tech_code', 'type', 'level_code','form_code', 'full_code']].drop_duplicates(subset=['tech_code', 'type'], keep='first')
     adb_df['eqn'] = adb_df.apply(eqn_func, axis=1)
     cap += '\n'.join(adb_df['eqn'].tolist())
     return cap


def Tech_CAP_generation_process(adb_file, nrun, cin_file_name = 'Tech_CAP.cin'):
    def tech_in_out_eqn(row):
        code = f"{row['tech_code']}___{row['level_code']}{row['form_code']} = "
        if row['type'] == 'main input':
            code += f"{row['full_code']}:inp"
        elif row['type'] == 'main output':
            code += f"{row['full_code']}:out"
        elif row['type'] == 'input':
            code += f"{row['full_code']}:inp * {row['full_code']}:ei{row['form_code']} / {row['full_code']}:ei{row['full_code'][1]}"
        elif row['type'] == 'output':
            code += f"{row['full_code']}:inp * {row['full_code']}:eo{row['form_code']}"
            if row['full_code'][1] != '.':
                code += f" / {row['full_code']}:ei{row['full_code'][1]}"
        return code
    def total_installed_cap_eqn(adb_tstep_df, adb_pll_df, adb_histcap_df, row):
        adb_pll_df = adb_pll_df.copy()[adb_pll_df['tech_code'] == row['tech_code']]
        adb_histcap_df = adb_histcap_df.copy()[adb_histcap_df['tech_code'] == row['tech_code']]
        default_pll = 25
        decommision_df = pd.DataFrame(
            [
                {
                    # some the hist cap to the value of the pll corresponding to this year, if year is old then get the first year in pll df
                    'start_year': r['year'],
                    'end_year': r['year'] + (adb_pll_df[adb_pll_df['year'] == adb_pll_df['year'].get(r['year'], adb_pll_df['year'].min())]['value'].values[0] if len(adb_pll_df) != 0 else default_pll),
                    'value': r['value']
                }
                if ((len(adb_pll_df[adb_pll_df['year'] == adb_pll_df['year'].get(r['year'], adb_pll_df['year'].min())]['value']) != 0) if len(adb_pll_df) != 0 else True)
                else {'year': np.nan, 'value': np.nan}
                
                for _, r in adb_histcap_df.iterrows()
            ])
        eqn = []
        for idx, tstep in adb_tstep_df[:-1].iterrows():
            e = f"{row['tech_code']}___{row['level_code']}{row['form_code']}_{tstep[0]} = "
            e += f"{row['full_code']}:yact:cum:sh>:#{idx+1:02d}:1{idx+1:02d} + "

            # Handle add historical cap
            for _, dc in decommision_df.iterrows():
                if dc['start_year'] < adb_tstep_df.loc[idx+1][0] < dc['end_year']:
                    e = e[:-3] if e[-3:] == ' + ' else e
                    e += f" + {dc['value']:g}"
                elif dc['start_year'] < adb_tstep_df.loc[idx][0] < dc['end_year']:
                    e = e[:-3] if e[-3:] == ' + ' else e
                    e += f" + {(dc['value'] * (dc['end_year']-tstep[0])/(adb_tstep_df.loc[idx+1][0]-tstep[0])):g}"

            # For subtracting the new cap added in the timeslices
            for j, inner_tstep in adb_tstep_df[:idx+1].iterrows():
                # I am at tstep, based on pll at each inner_tstep, exclude inner tstep if its pll has retired
                if len(adb_pll_df) != 0:
                    pll_value = adb_pll_df[adb_pll_df['year'] == inner_tstep[0]]['value'].values[0]
                else:
                    pll_value = default_pll
                inner_tstep_end_year = inner_tstep[0] + pll_value

                # print(f"{tstep[0]} | {inner_tstep[0]} | {pll_value} | {inner_tstep_end_year}")
                if tstep[0] < inner_tstep_end_year < adb_tstep_df.loc[idx+1][0]:
                    e = e[:-3] if e[-3:] == ' + ' else e
                    e += f" - {row['full_code']}:yact:prd:sh>:#{j+1:02d}:1{idx+1:02d}  * {(adb_tstep_df.loc[idx+1][0]-inner_tstep_end_year)/(adb_tstep_df.loc[idx+1][0]-tstep[0])}"
                elif inner_tstep_end_year <= tstep[0]:
                    e = e[:-3] if e[-3:] == ' + ' else e
                    e += f" - {row['full_code']}:yact:prd:sh>:#{j+1:02d}:1{idx+1:02d}"

            # in case the second loop never entered
            e = e[:-3] if e[-3:] == ' + ' else e
            e = e.replace(" =  + ", " = ")
            eqn.append(e)
        return '\n'.join(eqn)
    def fixed_cost_eqn(adb_tstep_df, adb_pll_df, adb_histcap_df, row):
        adb_pll_df = adb_pll_df.copy()[adb_pll_df['tech_code'] == row['tech_code']]
        adb_histcap_df = adb_histcap_df.copy()[adb_histcap_df['tech_code'] == row['tech_code']]
        default_pll = 25
        decommision_df = pd.DataFrame(
            [
                {
                    # some the hist cap to the value of the pll corresponding to this year, if year is old then get the first year in pll df
                    'start_year': r['year'],
                    'end_year': r['year'] + (adb_pll_df[adb_pll_df['year'] == adb_pll_df['year'].get(r['year'], adb_pll_df['year'].min())]['value'].values[0] if len(adb_pll_df) != 0 else default_pll),
                    'value': r['value']
                }
                if ((len(adb_pll_df[adb_pll_df['year'] == adb_pll_df['year'].get(r['year'], adb_pll_df['year'].min())]['value']) != 0) if len(adb_pll_df) != 0 else True)
                else {'year': np.nan, 'value': np.nan}
                
                for _, r in adb_histcap_df.iterrows()
            ])
        eqn = []
        for idx, tstep in adb_tstep_df[:-1].iterrows():
            e = f"{row['tech_code']}___{row['level_code']}{row['form_code']}_{tstep[0]} = {row['full_code']}:fom * ("
            e += f"{row['full_code']}:yact:cum:#{idx:02d}:1{idx+1:02d} + "

            # Handle add historical cap
            for _, dc in decommision_df.iterrows():
                if dc['start_year'] < adb_tstep_df.loc[idx+1][0] < dc['end_year']:
                    e = e[:-3] if e[-3:] == ' + ' else e
                    e += f" + {dc['value']:g}"
                elif dc['start_year'] < adb_tstep_df.loc[idx][0] < dc['end_year']:
                    e = e[:-3] if e[-3:] == ' + ' else e
                    e += f" + {(dc['value'] * (dc['end_year']-tstep[0])/(adb_tstep_df.loc[idx+1][0]-tstep[0])):g}"

            # For subtracting the new cap added in the timeslices
            for j, inner_tstep in adb_tstep_df[:idx+1].iterrows():
                # I am at tstep, based on pll at each inner_tstep, exclude inner tstep if its pll has retired
                if len(adb_pll_df) != 0:
                    pll_value = adb_pll_df[adb_pll_df['year'] == inner_tstep[0]]['value'].values[0]
                else:
                    pll_value = default_pll
                inner_tstep_end_year = inner_tstep[0] + pll_value

                # print(f"{tstep[0]} | {inner_tstep[0]} | {pll_value} | {inner_tstep_end_year}")
                if tstep[0] < inner_tstep_end_year < adb_tstep_df.loc[idx+1][0]:
                    e = e[:-3] if e[-3:] == ' + ' else e
                    e += f" - {row['full_code']}:yact:prd:sh>:#{j+1:02d}:1{idx+1:02d}  * {(adb_tstep_df.loc[idx+1][0]-inner_tstep_end_year)/(adb_tstep_df.loc[idx+1][0]-tstep[0])}"
                elif inner_tstep_end_year <= tstep[0]:
                    e = e[:-3] if e[-3:] == ' + ' else e
                    e += f" - {row['full_code']}:yact:prd:sh>:#{j+1:02d}:1{idx+1:02d}"

            # in case the second loop never entered
            e = e[:-3] if e[-3:] == ' + ' else e
            e = e.replace(" =  + ", " = ")
            e = e + ')'
            eqn.append(e)
        return '\n'.join(eqn)

    # Read ADB
    adb_df = read_adb_file(adb_file)
    adb_tstep_df = extract_adb_time_steps(adb_df, nrun)
    adb_pll_df = extract_adb_plant_life(adb_df)
    adb_histcap_df = extract_adb_historical_capacity(adb_df)
    adb_df = clean_up_adb(adb_df)

    cap = [
         f'title: Objective\nunit: , 1.\ndirection: hor\n@\nobj = func:act',
         generate_cap_table(title='Tech_in_out',
                            units='MWyr',
                            adb_df=adb_df,
                            only_output=False,
                            exclude_secondary_op_modes=False,
                            eqn_func=tech_in_out_eqn),
         generate_cap_table(title='Total_installed_cap',
                            units='MW',
                            adb_df=adb_df,
                            only_output=True,
                            exclude_secondary_op_modes=True,
                            eqn_func=lambda row: total_installed_cap_eqn(adb_tstep_df, adb_pll_df, adb_histcap_df, row)),
         generate_cap_table(title='New_installed_cap',
                            units='MW',
                            adb_df=adb_df,
                            only_output=True,
                            exclude_secondary_op_modes=True,
                            eqn_func=lambda row: f"{row['tech_code']}___{row['level_code']}{row['form_code']} = {row['full_code']}:yact"),
         generate_cap_table(title='Investments_per_unit',
                            units=' USD/kW',
                            adb_df=adb_df,
                            only_output=True,
                            exclude_secondary_op_modes=True,
                            eqn_func=lambda row: f"{row['tech_code']}___{row['level_code']}{row['form_code']} = {row['full_code']}:inv"),
         generate_cap_table(title='Investments_for_new_installations',
                            units='kUSD',
                            adb_df=adb_df,
                            only_output=True,
                            exclude_secondary_op_modes=True,
                            eqn_func=lambda row: f"{row['tech_code']}___{row['level_code']}{row['form_code']} = {row['full_code']}:inv * {row['full_code']}:yact"),
         generate_cap_table(title='Variable_cost_per_unit_of_output',
                            units='USD/kWyr',
                            adb_df=adb_df,
                            only_output=True,
                            exclude_secondary_op_modes=False,
                            eqn_func=lambda row: f"{row['tech_code']}___{row['level_code']}{row['form_code']} = {row['full_code']}:vom"),
         generate_cap_table(title='Variable_cost',
                            units='kUSD',
                            adb_df=adb_df,
                            only_output=True,
                            exclude_secondary_op_modes=False,
                            eqn_func=lambda row: f"{row['tech_code']}___{row['level_code']}{row['form_code']} = {row['full_code']}:vom * {row['full_code']}:out"),
         generate_cap_table(title='Fixed_cost_per_unit_of_output',
                            units='USD/kWyr',
                            adb_df=adb_df,
                            only_output=True,
                            exclude_secondary_op_modes=True,
                            eqn_func=lambda row: f"{row['tech_code']}___{row['level_code']}{row['form_code']} = {row['full_code']}:fom"),
         generate_cap_table(title='Fixed_cost',
                            units='kUSD',
                            adb_df=adb_df,
                            only_output=True,
                            exclude_secondary_op_modes=True,
                            eqn_func=lambda row: fixed_cost_eqn(adb_tstep_df, adb_pll_df, adb_histcap_df, row))
    ]

    cap_text = '\n@\n'.join(cap) + '\n@'

    with open(cin_file_name, 'w') as file:
        file.write(cap_text)
    print('Tech CAP file generated')


def LDR_CAP_generation_process(adb_file, cin_file_name = 'LDR_CAP.cin'):
    def LDR_eqn(adb_df, ldr_df, tech_ldc_df, row, season):
        adb_df = adb_df[adb_df['tech_code'] == row['tech_code']]
        ldr_type = adb_df['ldr_type'].iloc[0] if adb_df.shape[0] != 0 else np.nan
        tech_ldc_df = tech_ldc_df[tech_ldc_df['tech_code'] == row['tech_code']].reset_index(drop=True)
        ldr_df = pd.merge(ldr_df, tech_ldc_df['value'], left_index=True, right_index=True, how='left')
        ldr_df = ldr_df[ldr_df['season'] == season].reset_index(drop=True)

        eqn = []
        for _, ldr_row in ldr_df.iterrows():
            e = f"{row['tech_code']}___{row['level_code']}{row['form_code']}_{ldr_row['ts_code']} = "
            if ldr_type == 'moutp':
                e += f"{row['full_code']}:out * {ldr_row['value']:.6f} / {ldr_row['ts_length']:.6f}"
            else:
                e += f"{row['full_code']}......{ldr_row['ts_code']}:out / {ldr_row['ts_length']:.6f}"
            eqn.append(e)
        return '\n'.join(eqn)

    # Read ADB
    adb_df = read_adb_file(adb_file)
    ldr_df = extract_load_region(adb_df)
    tech_ldc_df = extract_tech_load_curves(adb_df)
    adb_df = clean_up_adb(adb_df)

    adb_df = adb_df[adb_df['hasldr'] & adb_df['type'].isin(['main output','output']) & (adb_df['level'] != 'Demand')]
    seasons = sorted(ldr_df['season'].unique())
    cap = []

    for s in seasons:
        cap.append(
            generate_cap_table(title=f'szn{s}',
                                units='MWyr',
                                adb_df=adb_df,
                                only_output=True,
                                exclude_secondary_op_modes=False,
                                precision=8,
                                eqn_func=lambda row: LDR_eqn(adb_df=adb_df, ldr_df=ldr_df, tech_ldc_df=tech_ldc_df, row=row, season=s)),
        )

    cap_text = '\n@\n'.join(cap) + '\n@'

    with open(cin_file_name, 'w') as file:
        file.write(cap_text)
    print('LDR CAP file generated')
