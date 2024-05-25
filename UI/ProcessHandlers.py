from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import Messagebox

import time
import pandas as pd
import threading
import traceback
import CAPGeneration.TechCAPFileGenerator as TechCAP
import CAPGeneration.LDRCAPFileGenerator as LDRCAP
import ResultsProcessing.ResultsProcessor as ResultsProcessor
import Utils.DataIO as DataIO
import DataProcessing.DataExtraction as Extractor
import DataProcessing.DataCleaning as Cleaner
import ADBProcessing.ADBProcessor as ADB
import Utils.Helper as Helper
import CostCalculator.CostProcessor as Coster

from UI import ProgressBarUtils as PBar
from UI import InputValidation as InpValidator
from UI import UIComponents as UIComp
from UI import GlobalState

def show_success_message(success_message):
    Messagebox.show_info(title="Process Completed", message=success_message)


def show_error_message(error_message):
    Messagebox.show_error(title="Process Error", message=error_message)


def generate_tech_cap(root, progress_bar, progress_label, time_label, start_time, adb_filepath, nrun, output_dir):
    start_time = time.time()
    stop_event = threading.Event()
    # Start the time update thread
    time_thread = threading.Thread(target=PBar.update_time_elapsed, args=(time_label, start_time, stop_event))
    time_thread.start()

    nrun = int(nrun)

    try:
        PBar.update_progress_bar(progress_bar, progress_label, time_label, 0, 100, 'Generating Tech CAP', start_time)
        TechCAP.Tech_CAP_generation_process(adb_filepath, nrun, output_dir)
    except Exception as e:
        # Stop the time update thread on error
        stop_event.set()
        time_thread.join()
        error_message = f"An error occurred:\n{traceback.format_exc()}"
        root.after(0, show_error_message, error_message)
        PBar.update_progress_bar(progress_bar, progress_label, time_label, 0, 100, 'Error in generating Tech CAP', start_time)
        # when error, reset the flag and re-enable buttons
        GlobalState.is_process_running = False
        UIComp.enable_buttons(root)
        raise(e)

    # Stop the time update thread when processing is done
    stop_event.set()
    time_thread.join()
    PBar.update_progress_bar(progress_bar, progress_label, time_label, 100, 100, 'Completed generating Tech CAP', start_time)
    root.after(0, show_success_message, 'Completed generating Tech CAP')

    # At the end of the function, reset the flag and re-enable buttons
    GlobalState.is_process_running = False
    UIComp.enable_buttons(root)


def generate_ldr_cap(root, progress_bar, progress_label, time_label, start_time, adb_filepath, nrun, output_dir):
    start_time = time.time()
    stop_event = threading.Event()
    # Start the time update thread
    time_thread = threading.Thread(target=PBar.update_time_elapsed, args=(time_label, start_time, stop_event))
    time_thread.start()

    nrun = int(nrun)

    try:
        PBar.update_progress_bar(progress_bar, progress_label, time_label, 0, 100, 'Generating LDR CAP', start_time)
        LDRCAP.LDR_CAP_generation_process(adb_filepath, nrun, output_dir)
    except Exception as e:
        # Stop the time update thread on error
        stop_event.set()
        time_thread.join()
        error_message = f"An error occurred:\n{traceback.format_exc()}"
        root.after(0, show_error_message, error_message)
        PBar.update_progress_bar(progress_bar, progress_label, time_label, 0, 100, 'Error in generating LDR CAP', start_time)
        # when error, reset the flag and re-enable buttons
        GlobalState.is_process_running = False
        UIComp.enable_buttons(root)
        raise(e)

    # Stop the time update thread when processing is done
    stop_event.set()
    time_thread.join()
    PBar.update_progress_bar(progress_bar, progress_label, time_label, 100, 100, 'Completed generating LDR CAP', start_time)
    root.after(0, show_success_message, 'Completed generating LDR CAP')

    # At the end of the function, reset the flag and re-enable buttons
    GlobalState.is_process_running = False
    UIComp.enable_buttons(root)


def process_results(root, progress_bar, progress_label, time_label, tech_results_entry, ldr_results_entry, template_entry, adb_entry, nrun, output_dir_entry, output_filename_entry, interpolate_var, with_cost_var):
    start_time = time.time()
    stop_event = threading.Event()
    # Start the time update thread
    time_thread = threading.Thread(target=PBar.update_time_elapsed, args=(time_label, start_time, stop_event))
    time_thread.start()

    tech_result_filepath = tech_results_entry.get()
    ldr_result_filepath = ldr_results_entry.get()
    tmpt_filepath = template_entry.get()
    adb_filepath = adb_entry.get()
    output_dir = output_dir_entry.get()
    output_filename = output_filename_entry.get()
    to_interpolate = interpolate_var.get()
    with_cost = with_cost_var.get()
    nrun = int(nrun)

    to_export = True
    num_stages = 3 if tech_result_filepath and ldr_result_filepath else 2
    if with_cost:
        num_stages += 1  # Additional stage for Cost calculation

    # Initial stage index for the export process
    stage_index = 0

    try:
        tech_file = pd.ExcelFile(tech_result_filepath) if tech_result_filepath else None
        ldr_file = pd.ExcelFile(ldr_result_filepath) if ldr_result_filepath else None
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
            stage_index += 1
            for idx, sheet in enumerate(tech_file.sheet_names):
                stage_progress = idx / len(tech_file.sheet_names) * 100 / num_stages
                msg = f'Processing Tech: {sheet}'
                print(msg)
                PBar.update_progress_bar(progress_bar, progress_label, time_label, stage_progress, 100, msg, start_time)
                processed_tables = ResultsProcessor.process_result_sheet(tech_file, sheet, tmpt_df, slice_types, adb_df, ldr_df, adb_pll_df, adb_full_tstep_df, nrun, is_interpolate=to_interpolate, sheet_type='TECH')
                combined_sheets = Helper.combine_sheets(combined_sheets, processed_tables, sheet)

        def cost_progress_callback(current, total, sheet, year):
            current_progress = (current / total) * (100 / num_stages)
            overall_progress = start_stage_progress + current_progress
            msg = f'Processing Cost: {sheet} ~ {year}'
            PBar.update_progress_bar(progress_bar, progress_label, time_label, overall_progress, 100, msg, start_time)

        if with_cost:
            stage_index += 1
            start_stage_progress = 100 / num_stages * (stage_index - 1)
            msg = f'Processing Cost Calculation...'
            print(msg)
            PBar.update_progress_bar(progress_bar, progress_label, time_label, start_stage_progress, 100, msg, start_time)
            combined_sheets = Coster.embed_costs(combined_sheets, tmpt_df, cost_progress_callback)

        if ldr_file:
            stage_index += 1
            for idx, sheet in enumerate(ldr_file.sheet_names):
                stage_progress = idx / len(ldr_file.sheet_names) * 100 / num_stages
                overall_progress = 100 * (1 / num_stages)  # Add previous stages' progress
                if with_cost:
                    overall_progress += 100 * (1 / num_stages)  # Add Cost stage progress
                overall_progress = overall_progress * (stage_index - 1) + stage_progress
                msg = f'Processing LDR: {sheet}'
                print(msg)
                PBar.update_progress_bar(progress_bar, progress_label, time_label, overall_progress, 100, msg, start_time)
                processed_tables = ResultsProcessor.process_result_sheet(ldr_file, sheet, tmpt_df, slice_types, adb_df, ldr_df, adb_pll_df, adb_full_tstep_df, nrun, is_interpolate=to_interpolate, sheet_type='LDR')
                for key in processed_tables:
                    # processed_tables[key] = processed_tables[key][processed_tables[key]['year'] == 2040]  # for testing only limit LDR to 1 year
                    combined_sheets[f'{sheet}_{key}_LDR'] = processed_tables[key]

        print()
        def update_export_progress(current, total, msg):
            stage_progress = (current / total) * (100 / num_stages)
            overall_progress = (100 / num_stages) * stage_index + stage_progress
            PBar.update_progress_bar(progress_bar, progress_label, time_label, overall_progress, 100, msg, start_time)

        if to_export:
            DataIO.export_dataframe_dict(output_filename, output_dir=output_dir, df_dict=combined_sheets, progress_callback=update_export_progress)

    except Exception as e:
        # Stop the time update thread on error
        stop_event.set()
        time_thread.join()
        error_message = f"An error occurred:\n{traceback.format_exc()}"
        root.after(0, show_error_message, error_message)
        PBar.update_progress_bar(progress_bar, progress_label, time_label, 0, 100, 'Error in processing results', start_time)
        # when error, reset the flag and re-enable buttons
        GlobalState.is_process_running = False
        UIComp.enable_buttons(root)
        raise(e)

    # Stop the time update thread when processing is done
    stop_event.set()
    time_thread.join()
    PBar.update_progress_bar(progress_bar, progress_label, time_label, 100, 100, 'Completed processing results', start_time)
    root.after(0, show_success_message, 'Completed processing results')
    print('\nCompleted!')

    # At the end of the function, reset the flag and re-enable buttons
    GlobalState.is_process_running = False
    UIComp.enable_buttons(root)


def start_generate_tech_cap(root, progress_bar, progress_label, time_label, adb_filepath, nrun, output_dir):
    if GlobalState.is_process_running:
        return  # Exit if another process is running

    if not InpValidator.validate_required_strings([adb_filepath, output_dir]) or not InpValidator.validate_nrun(nrun):
        Messagebox.show_error(title="Validation Error", message="Please ensure the ADB file is selected, nrun is a positive integer, and the output directory is selected.")
        return

    # Disable buttons and set flag
    UIComp.disable_buttons(root)
    GlobalState.is_process_running = True

    threading.Thread(target=generate_tech_cap, args=(root, progress_bar, progress_label, time_label, time.time(), adb_filepath, nrun, output_dir,), daemon=True).start()


def start_generate_ldr_cap(root, progress_bar, progress_label, time_label, adb_filepath, nrun, output_dir):
    if GlobalState.is_process_running:
        return  # Exit if another process is running

    if not InpValidator.validate_required_strings([adb_filepath, output_dir]) or not InpValidator.validate_nrun(nrun):
        Messagebox.show_error(title="Validation Error", message="Please ensure the ADB file is selected, nrun is a positive integer, and the output directory is selected.")
        return

    # Disable buttons and set flag
    UIComp.disable_buttons(root)
    GlobalState.is_process_running = True

    threading.Thread(target=generate_ldr_cap, args=(root, progress_bar, progress_label, time_label, time.time(), adb_filepath, nrun, output_dir,), daemon=True).start()


def start_result_processing_thread(root, progress_bar, progress_label, time_label, tech_results_entry, ldr_results_entry, template_entry, adb_entry, nrun, output_dir_entry, output_filename_entry, interpolate_var, with_cost_var):
    if GlobalState.is_process_running:
        return  # Exit if another process is running

    missing_entries = []
    if not adb_entry.get().strip():
        missing_entries.append("ADB file path")
    if not template_entry.get().strip():
        missing_entries.append("Template file path")
    if not output_filename_entry.get().strip():
        missing_entries.append("Output filename")

    tech_results_provided = tech_results_entry.get().strip()
    ldr_results_provided = ldr_results_entry.get().strip()
    with_cost_selected = with_cost_var.get()

    # Check if 'with_cost' is selected but Tech CAP results are not provided
    if with_cost_selected and not tech_results_provided:
        missing_entries.append("Tech Results (required for Cost Calculation)")

    # Check if 'tech_results_provided' but not nrun
    if tech_results_provided and not InpValidator.validate_nrun(nrun):
        missing_entries.append("nrun (required for processing tech results)")

    if missing_entries or not (tech_results_provided or ldr_results_provided):
        error_message = "Please ensure the following requirements are met:\n"
        if missing_entries:
            error_message += "- The following fields must be filled: " + ", ".join(missing_entries) + "\n"
        if not (tech_results_provided or ldr_results_provided):
            error_message += "- At least one of the Tech Results or LDR Results must be provided"

        Messagebox.show_error(title="Validation Error", message=error_message)
        return

    # Disable buttons and set flag
    UIComp.disable_buttons(root)
    GlobalState.is_process_running = True

    threading.Thread(target=process_results, args=(root, progress_bar, progress_label, time_label, tech_results_entry, ldr_results_entry, template_entry, adb_entry, nrun, output_dir_entry, output_filename_entry, interpolate_var, with_cost_var), daemon=True).start()
