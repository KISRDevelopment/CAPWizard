import Utils.DataIO as DataIO
import DataProcessing.DataExtraction as Extractor
import DataProcessing.DataTransformation as Transformer
import DataProcessing.DataEnrichment as Enricher
import DataProcessing.DataAnalysis as Analyzer


def process_result_sheet(filepath, sheet, tmpt_df, slice_types, adb_df, ldr_df, is_interpolate, is_LDR=False):
    result_df = DataIO.read_file(filepath, sheet)
    tables_list = Extractor.extract_tables(result_df=result_df)
    tables_dict = Transformer.process_tables(tables_list=tables_list)
    clean_tables_dict = Transformer.handle_duplicate_year_specified_data(tables_dict)
    template_enriched_tables_dict = Enricher.enrich_with_template(clean_tables_dict, tmpt_df)
    adb_enriched_tables_dict = Enricher.enrich_with_adb(adb_df=adb_df, tables_dict=template_enriched_tables_dict)
    ldr_enriched_tables_dict = Enricher.enrich_with_ldr(ldr_df=ldr_df, tables_dict=adb_enriched_tables_dict)
    enriched_tables_dict = Transformer.handle_impexp(ldr_enriched_tables_dict)

    if is_interpolate:
        interpolate_tables_dict = Transformer.interpolate_for_tables(enriched_tables_dict)
    else:
        interpolate_tables_dict = enriched_tables_dict

    if is_LDR:
        resulted_tables_dict = Enricher.embed_LDR_hour_and_type(interpolate_tables_dict, slice_types)
    else:
        balance_tables_dict = Analyzer.check_balance_for_tables(interpolate_tables_dict)
        balance_out_tables_dict = Analyzer.calc_tech_balance(balance_tables_dict)
        # resulted_tables_dict = Analyzer.calc_emissions(balance_out_tables_dict)
        resulted_tables_dict = balance_out_tables_dict

    transformed_tables_dict = Transformer.transform_tables(resulted_tables_dict)
    with_units_tables_dict = Enricher.add_units_column(transformed_tables_dict)
    converted_tables_dict = Enricher.add_Mtoe_value(with_units_tables_dict, convert_all=is_LDR)
    return converted_tables_dict


# def result_process(adb_filepath, tmpt_filepath, to_interpolate, tech_result_file=None, ldr_result_file=None, to_export=True, output_filename='Processed_results', output_dir=''):
#     tech_file = pd.ExcelFile(tech_result_file) if tech_result_file else None
#     ldr_file = pd.ExcelFile(ldr_result_file) if ldr_result_file else None
#     slice_types = DataIO.read_file(tmpt_filepath, 'Slices')
#     tmpt_df = DataIO.read_template_file(tmpt_filepath)
#     adb_df = DataIO.read_adb_file(adb_filepath)
#     ldr_df = Extractor.extract_load_region(adb_df)
#     adb_df = Cleaner.clean_up_adb(adb_df)
#     adb_df = ADB.process_adb(adb_df, tmpt_df)
#     combined_sheets = {}

#     if tech_file:
#         print('Processing Tech Results')
#         for sheet in tech_file.sheet_names:
#             print(f'\tProcessing sheet: {sheet}')
#             processed_tables = process_result_sheet(tech_file, sheet, tmpt_df, slice_types, adb_df, ldr_df, is_interpolate=to_interpolate, is_LDR=False)
#             combined_sheets = Helper.combine_sheets(combined_sheets, processed_tables, sheet)

#     if ldr_file:
#         print('Processing LDR Results')
#         for sheet in ldr_file.sheet_names:
#             print(f'\tProcessing sheet: {sheet}')
#             processed_tables = process_result_sheet(ldr_file, sheet, tmpt_df, slice_types, adb_df, ldr_df, is_interpolate=to_interpolate, is_LDR=True)
#             for key in processed_tables:
#                 # processed_tables[key] = processed_tables[key][processed_tables[key]['year'] == 2040]  # for testing only limit LDR to 1 year
#                 combined_sheets[f'{sheet}_{key}_LDR'] = processed_tables[key]

#     print()
#     if to_export:
#         DataIO.export_dataframe_dict(output_filename, output_dir=output_dir, df_dict=combined_sheets)
#     print('\nCompleted!')
