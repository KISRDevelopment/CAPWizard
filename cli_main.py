import pandas as pd

import Utils.DataIO as DataIO
import DataProcessing.DataExtraction as Extractor
import DataProcessing.DataCleaning as Cleaner
import ADBProcessing.ADBProcessor as ADB
import Utils.Helper as Helper
import ResultsProcessing.ResultsProcessor as ResultsProcessor
import CostCalculator.CostProcessor as Coster

from CAPGeneration.TechCAPFileGenerator import Tech_CAP_generation_process
from CAPGeneration.LDRCAPFileGenerator import LDR_CAP_generation_process


def result_process(adb_filepath, tmpt_filepath, to_interpolate, nrun, tech_result_file=None, ldr_result_file=None, with_cost=False, to_export=True, output_filename='Processed_results', output_dir=''):
    tech_file = pd.ExcelFile(tech_result_file) if tech_result_file else None
    ldr_file = pd.ExcelFile(ldr_result_file) if ldr_result_file else None
    slice_types = DataIO.read_file(tmpt_filepath, 'Slices')
    tmpt_df = DataIO.read_template_file(tmpt_filepath)
    adb_df = DataIO.read_adb_file(adb_filepath)
    ldr_df = Extractor.extract_load_region(adb_df)
    adb_full_tstep_df = Extractor.extract_adb_time_steps(adb_df)
    adb_pll_df = Extractor.extract_adb_plant_life(adb_df)
    adb_df = Cleaner.clean_up_adb(adb_df)
    adb_df = ADB.process_adb(adb_df, tmpt_df)
    combined_sheets = {}

    if tech_file:
        print('Processing Tech Results')
        for sheet in tech_file.sheet_names:
            print(f'\tProcessing sheet: {sheet}')
            processed_tables = ResultsProcessor.process_result_sheet(tech_file, sheet, tmpt_df, slice_types, adb_df, ldr_df, adb_pll_df, adb_full_tstep_df, nrun, is_interpolate=to_interpolate, sheet_type='TECH')
            combined_sheets = Helper.combine_sheets(combined_sheets, processed_tables, sheet)

    if with_cost:
        print('Processing Cost Calculation')
        combined_sheets = Coster.embed_costs(combined_sheets, tmpt_df)

    if ldr_file:
        print('Processing LDR Results')
        for idx, sheet in enumerate(ldr_file.sheet_names):
            # if idx != 0:  # for testing only limit LDR to 1 scenario
            #     continue
            print(f'\tProcessing sheet: {sheet}')
            processed_tables = ResultsProcessor.process_result_sheet(ldr_file, sheet, tmpt_df, slice_types, adb_df, ldr_df, adb_pll_df, adb_full_tstep_df, nrun, is_interpolate=to_interpolate, sheet_type='LDR')
            for key in processed_tables:
                # if key != 'szn1':  # for testing only limit LDR to 1 season
                #     continue
                # processed_tables[key] = processed_tables[key][processed_tables[key]['year'] == 2040]  # for testing only limit LDR to 1 year
                combined_sheets[f'{sheet}_{key}_LDR'] = processed_tables[key]

    print()
    if to_export:
        DataIO.export_dataframe_dict(output_filename, output_dir=output_dir, df_dict=combined_sheets)
    print('\nCompleted!')


if __name__ == "__main__":
    nrun = 11
    adb_filepath = 'Adb_file.adb'
    tmpt_filepath = 'Template.xlsx'
    tech_result_file = 'Raw_Tech_results.xlsx'
    ldr_result_file = 'Raw_LDR_results.xlsx'
    with_cost = True
    
    Tech_CAP_generation_process(adb_filepath=adb_filepath, nrun=nrun, output_dir=Helper.get_desktop_path())

    LDR_CAP_generation_process(adb_filepath=adb_filepath, nrun=nrun, output_dir=Helper.get_desktop_path())

    result_process(adb_filepath=adb_filepath,
                   tmpt_filepath=tmpt_filepath,
                   to_interpolate=False,
                   nrun=nrun,
                   tech_result_file=tech_result_file,
                   ldr_result_file=ldr_result_file,
                   with_cost=with_cost,
                   to_export=True,
                   output_filename='Processed_results',
                   output_dir=Helper.get_desktop_path())
