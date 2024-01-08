import time


def update_progress_bar(prog, label, time_label, current_prog, total_prog, msg, start_time):
    prog['value'] = round((current_prog / total_prog) * 100, 1)
    label.config(text=f"{msg} ({prog['value']}%)")
    update_time_display(time_label, start_time)


def update_time_display(time_label, start_time):
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = round(elapsed_time % 60, 1)
    time_label.config(text=f"Elapsed Time: {minutes:02d}:{seconds}")


def update_time_elapsed(time_label, start_time, stop_event):
    while not stop_event.is_set():
        update_time_display(time_label, start_time)
        time.sleep(0.1)
