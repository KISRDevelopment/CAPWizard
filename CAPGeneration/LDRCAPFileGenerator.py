import pandas as pd
import numpy as np
import CAPGeneration.CAPGenerator as CPTG
import DataProcessing.DataExtraction as Extractor
import DataProcessing.DataCleaning as Cleaner
import Utils.DataIO as DataIO
import os


def LDR_CAP_generation_process(adb_filepath, output_dir='', cin_file_name = 'LDR_CAP'):
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
    adb_df = DataIO.read_adb_file(adb_filepath)
    ldr_df = Extractor.extract_load_region(adb_df)
    tech_ldc_df = Extractor.extract_tech_load_curves(adb_df)
    adb_df = Cleaner.clean_up_adb(adb_df)

    adb_df = adb_df[adb_df['hasldr'] & adb_df['type'].isin(['main output','output']) & (adb_df['level'] != 'Demand')]
    seasons = sorted(ldr_df['season'].unique())
    cap = []

    for s in seasons:
        cap.append(
            CPTG.generate_cap_table(title=f'szn{s}',
                                units='MWyr',
                                adb_df=adb_df,
                                only_output=True,
                                exclude_secondary_op_modes=False,
                                precision=8,
                                eqn_func=lambda row: LDR_eqn(adb_df=adb_df, ldr_df=ldr_df, tech_ldc_df=tech_ldc_df, row=row, season=s)),
        )

    cap_text = '\n@\n'.join(cap) + '\n@'

    filepath = os.path.join(output_dir, cin_file_name+'.cin') if output_dir else cin_file_name+'.cin'

    with open(filepath, 'w') as file:
        file.write(cap_text)
    print('LDR CAP file generated')
