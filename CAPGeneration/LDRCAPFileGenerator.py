import pandas as pd
import numpy as np
import CAPGeneration.CAPGenerator as CPTG
import DataProcessing.DataExtraction as Extractor
import DataProcessing.DataEnrichment as Enricher
import DataProcessing.DataCleaning as Cleaner
import Utils.DataIO as DataIO
import Utils.Helper as Helper
import os

def build_eqn(ldr_df, row, ldr_type):
    eqn = []
    for _, ldr_row in ldr_df.iterrows():
        e = f"{row['tech_code']}___{row['level_code']}{row['form_code']}_{ldr_row['ts_code']} = "

        if row['type'] == 'main input':
            if ldr_type in ['moutp','demand']:
                e += f"{row['full_code']}:inp * {ldr_row['value']:.6f} / {ldr_row['ts_length']:.6f}"
            else:
                e += f"{row['full_code']}......{ldr_row['ts_code']}:inp / {ldr_row['ts_length']:.6f}"
        elif row['type'] == 'main output':
            if ldr_type in ['moutp','demand']:
                e += f"{row['full_code']}:out * {ldr_row['value']:.6f} / {ldr_row['ts_length']:.6f}"
            else:
                e += f"{row['full_code']}......{ldr_row['ts_code']}:out / {ldr_row['ts_length']:.6f}"
        elif row['type'] == 'input':
            if ldr_type in ['moutp','demand']:
                e += f"{row['full_code']}:inp * {row['full_code']}:ei{row['form_code']} / {row['full_code']}:ei{row['full_code'][1]}"
            else:
                e += f"{row['full_code']}......{ldr_row['ts_code']}:inp * {row['full_code']}:ei{row['form_code']} / {row['full_code']}:ei{row['full_code'][1]} / {ldr_row['ts_length']:.6f}"
        elif row['type'] == 'output':
            if ldr_type in ['moutp','demand']:
                e += f"{row['full_code']}:inp * {row['full_code']}:eo{row['form_code']} * {ldr_row['value']:.6f} / {ldr_row['ts_length']:.6f}"
                if row['full_code'][1] != '.':
                    e += f" / {row['full_code']}:ei{row['full_code'][1]}"
            else:
                e += f"{row['full_code']}......{ldr_row['ts_code']}:inp * {row['full_code']}:eo{row['form_code']} / {ldr_row['ts_length']:.6f}"
                if row['full_code'][1] != '.':
                    e += f" / {row['full_code']}:ei{row['full_code'][1]}"

        eqn.append(e)
    return '\n'.join(eqn)


def LDR_eqn(adb_df, ldr_df, tech_ldc_df, row, season):
    adb_df = adb_df[adb_df['tech_code'] == row['tech_code']]
    ldr_type = adb_df['ldr_type'].iloc[0] if adb_df.shape[0] != 0 else np.nan

    if ldr_type == 'demand':
        energy_code = str(row['mout_code']) + '-' + str(row['mout_lvl_code'])
        tech_ldc_df = tech_ldc_df[tech_ldc_df['key'] == energy_code].reset_index(drop=True)
    else:
        tech_ldc_df = tech_ldc_df[tech_ldc_df['tech_code'] == row['tech_code']].reset_index(drop=True)

    ldr_df = pd.merge(ldr_df, tech_ldc_df['value'], left_index=True, right_index=True, how='left')
    ldr_df = ldr_df[ldr_df['season'] == season].reset_index(drop=True)

    return build_eqn(ldr_df, row, ldr_type)


def LDR_CAP_generation_process(adb_filepath, nrun, output_dir='', cin_file_name = 'LDR_CAP'):
    # Read ADB
    adb_df = DataIO.read_adb_file(adb_filepath)
    ldr_df = Extractor.extract_load_region(adb_df)
    tech_ldc_df = Extractor.extract_tech_load_curves(adb_df)
    demand_codes = Extractor.extract_demand_codes(adb_df)
    tech_fyear = Extractor.extract_tech_fyear(adb_df)
    last_tstep_year = Extractor.extract_adb_time_steps(adb_df).iloc[nrun-1][0]
    adb_df = Cleaner.clean_up_adb(adb_df)
    adb_df = Enricher.apply_demand_ldr_type_on_adb(adb_df, demand_codes)

    # Filter only the technologies that has LDR
    adb_df = adb_df[adb_df['hasldr']]

    # Filter techs where fyear is beyond study period
    tech_out_of_period = tech_fyear[tech_fyear['fyear'] > last_tstep_year]

    # Extract base tech code and checl if it is in tech out of period list
    is_in_out_of_period = adb_df['tech_code'].apply(Helper.extract_base_tech_code).isin(tech_out_of_period['tech_code'])

    # Drop the rows where base tech code is in out of period tech codes
    adb_df = adb_df[~is_in_out_of_period]

    seasons = sorted(ldr_df['season'].unique())
    cap = []

    for s in seasons:
        cap.append(
            CPTG.generate_cap_table(title=f'szn{s}',
                                units='MWyr',
                                adb_df=adb_df,
                                only_output=False,
                                exclude_secondary_op_modes=False,
                                precision=8,
                                eqn_func=lambda row: LDR_eqn(adb_df=adb_df, ldr_df=ldr_df, tech_ldc_df=tech_ldc_df, row=row, season=s)),
        )

    cap_text = '\n@\n'.join(cap) + '\n@'

    filepath = os.path.join(output_dir, cin_file_name+'.cin') if output_dir else cin_file_name+'.cin'

    with open(filepath, 'w') as file:
        file.write(cap_text)
    print('LDR CAP file generated')
