import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter.filedialog import askopenfile, askdirectory

import Utils.Helper as Helper
from UI import ProcessHandlers
from UI import GlobalState

import requests

import threading
import webbrowser

APP_VERSION = 'v20241115'

def select_file(entry):
    file_obj = askopenfile()
    if file_obj:
        file_path = file_obj.name
        entry.delete(0, ttk.END)
        entry.insert(0, file_path)


def select_dir(entry):
    filedir = askdirectory()
    entry.delete(0, ttk.END)
    entry.insert(0, filedir)


# Function to create vertical labels
def create_vertical_label(parent, text, padx=10):
    label = ttk.Label(parent, text=text, font=("Helvetica", 16))
    label.pack(side=ttk.LEFT, padx=padx, fill='y')
    label.update()
    label.config(wraplength=label.winfo_height())  # Wrap text to the label's height
    return label


def enable_buttons(root):
    root.after(0, lambda: root.generate_tech_button.config(state=ttk.NORMAL))
    root.after(0, lambda: root.generate_ldr_button.config(state=ttk.NORMAL))
    root.after(0, lambda: root.process_button.config(state=ttk.NORMAL))


def disable_buttons(root):
    root.generate_tech_button.config(state=ttk.DISABLED)
    root.generate_ldr_button.config(state=ttk.DISABLED)
    root.process_button.config(state=ttk.DISABLED)


def check_for_updates(version_label):
    readme_url = "https://raw.githubusercontent.com/KISRDevelopment/CAPWizard/master/readme.md"

    try:
        response = requests.get(readme_url)
        content = response.text

        # Find the line containing the version number
        for line in content.split("\n"):
            if "Current Version:" in line:
                latest_version = line.split(":")[-1].strip()
                break

        if APP_VERSION != latest_version:
            version_label.config(text=APP_VERSION, foreground="red")
            version_label.bind("<Enter>", lambda e: version_label.config(text="Update available!", cursor="hand2"))
            version_label.bind("<Leave>", lambda e: version_label.config(text=APP_VERSION, cursor=""))
            version_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/KISRDevelopment/CAPWizard"))
    except Exception as e:
        print(f"Error checking for updates: {e}")


def create_ui(root):

    # Title Label
    title_label = ttk.Label(root, text="CAP Wizard", font=("Helvetica", 32))
    title_label.pack(pady=(10, 5))

    # Section 1
    section1_frame = ttk.Frame(root)
    create_vertical_label(section1_frame, "STEP 1")

    # ADB File Selection and nrun in one row
    file_selection_frame = ttk.Frame(section1_frame)
    adb_frame = ttk.Frame(file_selection_frame)
    nrun_frame = ttk.Frame(file_selection_frame)

    # ADB File Selection
    adb_label = ttk.Label(adb_frame, text="ADB file:")
    adb_entry = ttk.Entry(adb_frame, width=10)
    adb_browse_button = ttk.Button(adb_frame, text="Browse", command=lambda: select_file(adb_entry))
    adb_label.pack(side=ttk.LEFT)
    adb_entry.pack(side=ttk.LEFT, fill='x', expand=True)
    adb_browse_button.pack(side=ttk.LEFT)

    # Number of Runs
    nrun_label = ttk.Label(nrun_frame, text="Number of Runs:")
    nrun_entry = ttk.Entry(nrun_frame, width=5)
    nrun_label.pack(side=ttk.LEFT)
    nrun_entry.pack(side=ttk.LEFT)
    
    # Output Directory Selection
    output_dir_frame = ttk.Frame(section1_frame)
    output_dir_label = ttk.Label(output_dir_frame, text="Output dir:")
    output_dir_entry = ttk.Entry(output_dir_frame, width=20)
    output_dir_entry.insert(0, Helper.get_desktop_path())
    output_dir_browse_button = ttk.Button(output_dir_frame, text="Browse", command=lambda: select_dir(output_dir_entry))
    output_dir_label.pack(side=ttk.LEFT)
    output_dir_entry.pack(side=ttk.LEFT, fill="x", expand=True)
    output_dir_browse_button.pack(side=ttk.LEFT)

    adb_frame.pack(side=ttk.LEFT, padx=10, fill='x', expand=True)
    nrun_frame.pack(side=ttk.LEFT, padx=10)
    file_selection_frame.pack(padx=5, pady=5, fill='x', expand=True)
    output_dir_frame.pack(padx=10, pady=5, fill="x", expand=True)
    section1_frame.pack(padx=5, pady=5, fill="x", expand=True)

    # Seperator between sections
    sep_line = ttk.Separator()
    sep_line.pack(pady= 5, fill="x", expand=True)

    # Section 2
    section2_frame = ttk.Frame(root)
    create_vertical_label(section2_frame, "STEP 2")

    # CAP Generation Buttons
    cap_frame = ttk.Frame(section2_frame)
    root.generate_ldr_button = ttk.Button(cap_frame,
                                          text="Generate LDR CAP",
                                          command=lambda: ProcessHandlers.start_generate_ldr_cap(root,
                                                                                                  progress_bar,
                                                                                                  progress_label,
                                                                                                  time_label,
                                                                                                  adb_entry.get(),
                                                                                                  nrun_entry.get(),
                                                                                                  output_dir_entry.get()),
                                        state=ttk.NORMAL if not GlobalState.is_process_running else ttk.DISABLED)
    root.generate_tech_button = ttk.Button(cap_frame,
                                           text="Generate Tech CAP",
                                           command=lambda: ProcessHandlers.start_generate_tech_cap(root,
                                                                                                   progress_bar,
                                                                                                   progress_label,
                                                                                                   time_label,
                                                                                                   adb_entry.get(),
                                                                                                   nrun_entry.get(),
                                                                                                   output_dir_entry.get()),
                                            state=ttk.NORMAL if not GlobalState.is_process_running else ttk.DISABLED)
    root.generate_tech_button.pack(side=ttk.TOP, padx=5, pady=10)
    root.generate_ldr_button.pack(side=ttk.BOTTOM, padx=5, pady=10)

    cap_frame.pack()
    section2_frame.pack(padx=5, pady=5, fill="x", expand=True)

    # Seperator between sections
    sep_line = ttk.Separator()
    sep_line.pack(pady= 5, fill="x", expand=True)

    # Section 3
    section3_frame = ttk.Frame(root)
    create_vertical_label(section3_frame, "STEP 3")

    # Template, Tech Results, and LDR Results Selection
    results_frame = ttk.Frame(section3_frame)
    template_frame = ttk.Frame(results_frame)
    tech_results_frame = ttk.Frame(results_frame)
    ldr_results_frame = ttk.Frame(results_frame)

    # Template File Selection
    template_label = ttk.Label(template_frame, text="Template File:")
    template_entry = ttk.Entry(template_frame, width=10)
    template_browse_button = ttk.Button(template_frame, text="Browse", command=lambda: select_file(template_entry))
    template_label.pack(side=ttk.LEFT)
    template_entry.pack(side=ttk.LEFT, fill='x', expand=True)
    template_browse_button.pack(side=ttk.LEFT)

    # Tech Results File Selection
    tech_results_label = ttk.Label(tech_results_frame, text="Tech Results:")
    tech_results_entry = ttk.Entry(tech_results_frame, width=10)
    tech_results_browse_button = ttk.Button(tech_results_frame, text="Browse", command=lambda: select_file(tech_results_entry))
    tech_results_label.pack(side=ttk.LEFT)
    tech_results_entry.pack(side=ttk.LEFT, fill='x', expand=True)
    tech_results_browse_button.pack(side=ttk.LEFT)

    # LDR Results File Selection
    ldr_results_label = ttk.Label(ldr_results_frame, text="LDR Results:")
    ldr_results_entry = ttk.Entry(ldr_results_frame, width=10)
    ldr_results_browse_button = ttk.Button(ldr_results_frame, text="Browse", command=lambda: select_file(ldr_results_entry))
    ldr_results_label.pack(side=ttk.LEFT)
    ldr_results_entry.pack(side=ttk.LEFT, fill='x', expand=True)
    ldr_results_browse_button.pack(side=ttk.LEFT)

    # Interpolate Checkbox
    interpolate_var = ttk.BooleanVar()
    interpolate_check = ttk.Checkbutton(results_frame, text="Interpolate", variable=interpolate_var)

    # with cost calculation Checkbox
    with_cost_var = ttk.BooleanVar()
    with_cost_check = ttk.Checkbutton(results_frame, text="Cost Calculations", variable=with_cost_var)

    # Output Filename Entry
    output_filename_frame = ttk.Frame(results_frame)
    output_filename_label = ttk.Label(output_filename_frame, text="Output Filename:")
    output_filename_entry = ttk.Entry(output_filename_frame, width=20)
    output_filename_entry.insert(0, 'Processed_results')  # Setting default text
    output_filename_label.pack(side=ttk.LEFT)
    output_filename_entry.pack(side=ttk.LEFT, fill='x', expand=True)

    # Processing Button
    root.process_button = ttk.Button(results_frame,
                                     text="Start Processing",
                                     command=lambda:ProcessHandlers.start_result_processing_thread(root,
                                                                                                   progress_bar,
                                                                                                   progress_label,
                                                                                                   time_label,
                                                                                                   tech_results_entry,
                                                                                                   ldr_results_entry,
                                                                                                   template_entry,
                                                                                                   adb_entry,
                                                                                                   nrun_entry.get(),
                                                                                                   output_dir_entry,
                                                                                                   output_filename_entry,
                                                                                                   interpolate_var,
                                                                                                   with_cost_var),
                                     state=ttk.NORMAL if not GlobalState.is_process_running else ttk.DISABLED)

    template_frame.pack(side=ttk.TOP, padx=10, pady=5, fill='x', expand=True)
    tech_results_frame.pack(side=ttk.TOP, padx=10, pady=5, fill='x', expand=True)
    ldr_results_frame.pack(side=ttk.TOP, padx=10, pady=5, fill='x', expand=True)
    interpolate_check.pack(side=ttk.TOP, pady=5)
    with_cost_check.pack(side=ttk.TOP, pady=5)
    output_filename_frame.pack(side=ttk.TOP, padx=10, pady=5, fill='x', expand=True)
    root.process_button.pack(pady=5)
    results_frame.pack(side=ttk.TOP, padx=10, pady=5, fill='x', expand=True)
    section3_frame.pack(padx=5, pady=5, fill="x", expand=True)

    # Seperator between sections
    sep_line = ttk.Separator()
    sep_line.pack(pady= 5, fill="x", expand=True)

    # Progress Bar and Timer
    progress_frame = ttk.Frame(root)
    progress_bar = ttk.Progressbar(progress_frame, orient=ttk.HORIZONTAL, length=400, mode='determinate')
    progress_label = ttk.Label(progress_frame, text="Progress:")
    time_label = ttk.Label(progress_frame, text="Elapsed Time: 00:00.0")
    progress_bar.pack(fill='x', expand=True)
    progress_label.pack()
    time_label.pack()
    progress_frame.pack(padx=10, pady=5, fill='x', expand=True)

    # Seperator between sections
    sep_line = ttk.Separator()
    sep_line.pack(pady= (5,0), fill="x", expand=True)

    # Copyright Label
    copyright_label = ttk.Label(root, text="Developed by: Yousef S. Al-Qattan - Kuwait Institute for Scientific Research", font=("Helvetica", 12))
    copyright_label.pack(side=ttk.LEFT, padx=5, pady=5)
 
    # Version Label
    version_label = ttk.Label(root, text=APP_VERSION, font=("Helvetica", 12))
    version_label.pack(side=ttk.RIGHT, padx=5, pady=5)

    # Start the update check in a separate thread
    update_thread = threading.Thread(target=check_for_updates, args=(version_label,))
    update_thread.daemon = True  # Mark the thread as a daemon so it exits when the main program exits
    update_thread.start()

    root.mainloop()
