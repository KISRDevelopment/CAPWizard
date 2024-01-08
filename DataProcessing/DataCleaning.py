import pandas as pd
import DataProcessing.DataExtraction as Extractor


def clean_up_adb(adb_df):
    adb_df = adb_df.copy()
    energy_forms_lookup = Extractor.extract_adb_energy_forms(adb_df)
    energy_systems_lookup = Extractor.extract_adb_systems(adb_df)
    tech_ldc_df = Extractor.extract_tech_load_curves(adb_df)
    adb_df = pd.merge(energy_systems_lookup, energy_forms_lookup, on='fuel_code', how='left')
    adb_df = adb_df.drop('fuel_code', axis=1)
    adb_df = Extractor.insert_technology_code(adb_df)
    adb_df = pd.merge(adb_df, tech_ldc_df[['tech_code','ldr_type']].drop_duplicates(), on='tech_code', how='left')
    adb_df = adb_df[['tech_code','type','activity_code','hasldr','ldr_type','level','form','form_code',
                     'level_code','mout_code','minp_code','mout_lvl_code','full_code']]  # new col order
    return adb_df
