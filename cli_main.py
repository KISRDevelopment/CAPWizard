import pandas as pd

import Utils.DataIO as DataIO
import DataProcessing.DataExtraction as Extractor
import DataProcessing.DataCleaning as Cleaner
import ADBProcessing.ADBProcessor as ADB
import Utils.Helper as Helper
import ResultsProcessing.ResultsProcessor as ResultsProcessor


def result_process(adb_filepath, tmpt_filepath, to_interpolate, tech_result_file=None, ldr_result_file=None, to_export=True, output_filename='Processed_results', output_dir=''):
    tech_file = pd.ExcelFile(tech_result_file) if tech_result_file else None
    ldr_file = pd.ExcelFile(ldr_result_file) if ldr_result_file else None
    slice_types = DataIO.read_file(tmpt_filepath, 'Slices')
    tmpt_df = DataIO.read_template_file(tmpt_filepath)
    adb_df = DataIO.read_adb_file(adb_filepath)
    ldr_df = Extractor.extract_load_region(adb_df)
    adb_df = Cleaner.clean_up_adb(adb_df)
    adb_df = ADB.process_adb(adb_df, tmpt_df)
    combined_sheets = {}

    if tech_file:
        print('Processing Tech Results')
        for sheet in tech_file.sheet_names:
            print(f'\tProcessing sheet: {sheet}')
            processed_tables = ResultsProcessor.process_result_sheet(tech_file, sheet, tmpt_df, slice_types, adb_df, ldr_df, is_interpolate=to_interpolate, is_LDR=False)
            combined_sheets = Helper.combine_sheets(combined_sheets, processed_tables, sheet)

    if ldr_file:
        print('Processing LDR Results')
        for idx, sheet in enumerate(ldr_file.sheet_names):
            # if idx != 0:  # for testing only limit LDR to 1 scenario
            #     continue
            print(f'\tProcessing sheet: {sheet}')
            processed_tables = ResultsProcessor.process_result_sheet(ldr_file, sheet, tmpt_df, slice_types, adb_df, ldr_df, is_interpolate=to_interpolate, is_LDR=True)
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
    result_process(adb_filepath='Adb_file.adb',
                   tmpt_filepath='Template.xlsx',
                   to_interpolate=False,
                   tech_result_file=None,
                   ldr_result_file='Raw_LDR_results.xlsx',
                   to_export=True,
                   output_filename='Processed_results',
                   output_dir=Helper.get_desktop_path())