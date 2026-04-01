# ============================================================
# Auto File Organizer - Professional Tkinter Desktop App
# ============================================================
# Beginner-friendly single-file project
# Safe file organizer with modern multi-page UI
# It does NOT delete files, only moves them safely
# Uses threading so the GUI does not freeze on large folders

import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime


# ------------------------------------------------------------
# Global variables
# ------------------------------------------------------------
selected_folder = ""
total_files = 0
organized_files = 0
skipped_files = 0
is_processing = False
current_page = "Home"

# App settings
settings_data = {
    "theme": "Default",
    "confirm_before_organizing": True,
    "log_timestamps": True,
    "recursive_scan": False,
    "auto_open_log": False,
    "skip_hidden_files": False,
    "window_mode": "Resizable"
}

# File categories
FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png"],
    "Videos": [".mp4", ".mkv"],
    "Documents": [".pdf", ".docx", ".txt"],
    "Audio": [".mp3", ".wav"],
    "Archives": [".zip", ".rar"],
    "Programs": [".exe"],
}


# ------------------------------------------------------------
# Theme colors
# ------------------------------------------------------------
THEMES = {
    "Default": {
        "root_bg": "#eef3f8",
        "sidebar_bg": "#dfe8f3",
        "sidebar_fg": "#1f2937",
        "sidebar_muted": "#6b7280",
        "sidebar_hover": "#cfdceb",
        "sidebar_active": "#3b82f6",
        "sidebar_active_fg": "#ffffff",
        "content_bg": "#ffffff",
        "header_fg": "#111827",
        "subtext_fg": "#6b7280",
        "card1_bg": "#eef6ff",
        "card2_bg": "#ecfdf3",
        "card3_bg": "#fff4e5",
        "box_bg": "#f8fafc",
        "box_fg": "#374151",
        "log_bg": "#f8fafc",
        "log_fg": "#374151",
        "status_bg": "#e5edf5",
        "status_fg": "#374151",
        "primary_btn": "#3b82f6",
        "primary_btn_hover": "#2563eb",
        "success_btn": "#10b981",
        "success_btn_hover": "#059669",
        "neutral_btn": "#e5e7eb",
        "neutral_btn_hover": "#d1d5db",
        "danger_btn": "#ef4444",
        "danger_btn_hover": "#dc2626",
        "card_value_fg": "#111827",
        "card_title_fg": "#4b5563",
        "border_color": "#dbe3ec",
        "progress_trough": "#dfe7f2",
        "progress_bar": "#3b82f6",
        "entry_bg": "#ffffff",
    },
    "Light": {
        "root_bg": "#f5f7fb",
        "sidebar_bg": "#ffffff",
        "sidebar_fg": "#111827",
        "sidebar_muted": "#6b7280",
        "sidebar_hover": "#f2f4f7",
        "sidebar_active": "#2563eb",
        "sidebar_active_fg": "#ffffff",
        "content_bg": "#ffffff",
        "header_fg": "#111827",
        "subtext_fg": "#6b7280",
        "card1_bg": "#f3f8ff",
        "card2_bg": "#f0fdf4",
        "card3_bg": "#fff7ed",
        "box_bg": "#f9fafb",
        "box_fg": "#374151",
        "log_bg": "#f9fafb",
        "log_fg": "#374151",
        "status_bg": "#f3f4f6",
        "status_fg": "#374151",
        "primary_btn": "#2563eb",
        "primary_btn_hover": "#1d4ed8",
        "success_btn": "#16a34a",
        "success_btn_hover": "#15803d",
        "neutral_btn": "#e5e7eb",
        "neutral_btn_hover": "#d1d5db",
        "danger_btn": "#ef4444",
        "danger_btn_hover": "#dc2626",
        "card_value_fg": "#111827",
        "card_title_fg": "#4b5563",
        "border_color": "#e5e7eb",
        "progress_trough": "#e5e7eb",
        "progress_bar": "#2563eb",
        "entry_bg": "#ffffff",
    },
    "Dark": {
        "root_bg": "#0f172a",
        "sidebar_bg": "#111827",
        "sidebar_fg": "#e5e7eb",
        "sidebar_muted": "#94a3b8",
        "sidebar_hover": "#1f2937",
        "sidebar_active": "#2563eb",
        "sidebar_active_fg": "#ffffff",
        "content_bg": "#1e293b",
        "header_fg": "#f8fafc",
        "subtext_fg": "#cbd5e1",
        "card1_bg": "#1d4b7a",
        "card2_bg": "#14532d",
        "card3_bg": "#78350f",
        "box_bg": "#0f172a",
        "box_fg": "#e5e7eb",
        "log_bg": "#0f172a",
        "log_fg": "#e5e7eb",
        "status_bg": "#111827",
        "status_fg": "#e5e7eb",
        "primary_btn": "#3b82f6",
        "primary_btn_hover": "#2563eb",
        "success_btn": "#10b981",
        "success_btn_hover": "#059669",
        "neutral_btn": "#334155",
        "neutral_btn_hover": "#475569",
        "danger_btn": "#ef4444",
        "danger_btn_hover": "#dc2626",
        "card_value_fg": "#f8fafc",
        "card_title_fg": "#e2e8f0",
        "border_color": "#334155",
        "progress_trough": "#334155",
        "progress_bar": "#3b82f6",
        "entry_bg": "#111827",
    }
}


# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def center_window(win, width, height):
    """Center the window on the screen."""
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")


def truncate_path(path, max_length=80):
    """Shorten long folder path for display."""
    if len(path) <= max_length:
        return path
    return path[:35] + "..." + path[-40:]


def is_hidden_file(file_name):
    """Check hidden file by name."""
    return file_name.startswith(".")


def update_status(message):
    """Update status labels."""
    status_var.set(message)
    home_status_var.set(message)


def update_stats():
    """Update stat cards."""
    total_files_var.set(str(total_files))
    organized_files_var.set(str(organized_files))
    skipped_files_var.set(str(skipped_files))


def log_message(message):
    """Add text to log box."""
    if settings_data["log_timestamps"]:
        now = datetime.now().strftime("%H:%M:%S")
        final_text = f"[{now}] {message}\n"
    else:
        final_text = f"{message}\n"

    log_box.insert(tk.END, final_text)
    log_box.see(tk.END)


def get_unique_filename(destination_folder, filename):
    """
    Safe duplicate rename:
    file.txt -> file(1).txt -> file(2).txt
    """
    name, ext = os.path.splitext(filename)
    new_filename = filename
    counter = 1

    while os.path.exists(os.path.join(destination_folder, new_filename)):
        new_filename = f"{name}({counter}){ext}"
        counter += 1

    return new_filename


def get_destination_folder(file_name, base_folder):
    """Return correct category folder."""
    ext = os.path.splitext(file_name)[1].lower()

    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return os.path.join(base_folder, category)

    return os.path.join(base_folder, "Others")


def safe_button_hover(widget, normal_color, hover_color, fg):
    """Simple hover effect."""
    def on_enter(event):
        widget.config(bg=hover_color, cursor="hand2")

    def on_leave(event):
        widget.config(bg=normal_color, fg=fg)

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


def apply_window_mode():
    """Apply fixed or resizable mode."""
    if settings_data["window_mode"] == "Resizable":
        root.resizable(True, True)
    else:
        root.resizable(False, False)


# ------------------------------------------------------------
# Page switching
# ------------------------------------------------------------
def show_page(page_name):
    """Switch page in main content area."""
    global current_page
    current_page = page_name

    home_page.pack_forget()
    organize_page.pack_forget()
    logs_page.pack_forget()
    settings_page.pack_forget()

    if page_name == "Home":
        home_page.pack(fill="both", expand=True)
        page_title_var.set("Welcome Back")
        page_subtitle_var.set("Manage and organize your files safely with a clean desktop interface.")
    elif page_name == "Organize":
        organize_page.pack(fill="both", expand=True)
        page_title_var.set("Organize Files")
        page_subtitle_var.set("Choose a folder and sort files safely into category folders.")
    elif page_name == "Logs":
        logs_page.pack(fill="both", expand=True)
        page_title_var.set("Activity Logs")
        page_subtitle_var.set("Review moved files, skipped items, completion messages, and errors.")
    elif page_name == "Settings":
        settings_page.pack(fill="both", expand=True)
        page_title_var.set("Settings")
        page_subtitle_var.set("Control the appearance and behavior of your application.")

    update_sidebar_buttons()


def update_sidebar_buttons():
    """Highlight active sidebar button."""
    colors = THEMES[settings_data["theme"]]

    button_map = {
        "Home": btn_home,
        "Organize": btn_organize,
        "Logs": btn_logs,
        "Settings": btn_settings
    }

    for name, button in button_map.items():
        if name == current_page:
            button.config(
                bg=colors["sidebar_active"],
                fg=colors["sidebar_active_fg"],
                activebackground=colors["sidebar_active"],
                activeforeground=colors["sidebar_active_fg"]
            )
        else:
            button.config(
                bg=colors["sidebar_bg"],
                fg=colors["sidebar_fg"],
                activebackground=colors["sidebar_hover"],
                activeforeground=colors["sidebar_fg"]
            )


# ------------------------------------------------------------
# Theme system
# ------------------------------------------------------------
def apply_theme():
    """Apply selected theme to UI."""
    colors = THEMES[settings_data["theme"]]

    root.configure(bg=colors["root_bg"])
    main_container.config(bg=colors["root_bg"])

    sidebar.config(bg=colors["sidebar_bg"])
    content_area.config(bg=colors["content_bg"])
    header_frame.config(bg=colors["content_bg"])
    page_container.config(bg=colors["content_bg"])

    app_name_label.config(bg=colors["sidebar_bg"], fg=colors["sidebar_fg"])
    menu_title_label.config(bg=colors["sidebar_bg"], fg=colors["sidebar_muted"])
    sidebar_note_label.config(bg=colors["sidebar_bg"], fg=colors["sidebar_muted"])

    page_title_label.config(bg=colors["content_bg"], fg=colors["header_fg"])
    page_subtitle_label.config(bg=colors["content_bg"], fg=colors["subtext_fg"])

    status_bar.config(bg=colors["status_bg"], fg=colors["status_fg"])

    for page in [home_page, organize_page, logs_page, settings_page]:
        page.config(bg=colors["content_bg"])

    # Home
    home_top_frame.config(bg=colors["content_bg"])
    home_welcome_title.config(bg=colors["content_bg"], fg=colors["header_fg"])
    home_welcome_subtitle.config(bg=colors["content_bg"], fg=colors["subtext_fg"])
    home_cards_frame.config(bg=colors["content_bg"])

    total_card.config(bg=colors["card1_bg"], highlightbackground=colors["border_color"], highlightcolor=colors["border_color"])
    organized_card.config(bg=colors["card2_bg"], highlightbackground=colors["border_color"], highlightcolor=colors["border_color"])
    skipped_card.config(bg=colors["card3_bg"], highlightbackground=colors["border_color"], highlightcolor=colors["border_color"])

    total_value_label.config(bg=colors["card1_bg"], fg=colors["card_value_fg"])
    total_title_label.config(bg=colors["card1_bg"], fg=colors["card_title_fg"])
    organized_value_label.config(bg=colors["card2_bg"], fg=colors["card_value_fg"])
    organized_title_label.config(bg=colors["card2_bg"], fg=colors["card_title_fg"])
    skipped_value_label.config(bg=colors["card3_bg"], fg=colors["card_value_fg"])
    skipped_title_label.config(bg=colors["card3_bg"], fg=colors["card_title_fg"])

    home_status_box.config(bg=colors["box_bg"], highlightbackground=colors["border_color"], highlightcolor=colors["border_color"])
    home_status_title.config(bg=colors["box_bg"], fg=colors["header_fg"])
    home_status_label.config(bg=colors["box_bg"], fg=colors["box_fg"])

    # Organize
    organize_info_box.config(bg=colors["box_bg"], highlightbackground=colors["border_color"], highlightcolor=colors["border_color"])
    organize_info_title.config(bg=colors["box_bg"], fg=colors["header_fg"])
    organize_info_text.config(bg=colors["box_bg"], fg=colors["box_fg"])

    folder_frame.config(bg=colors["content_bg"])
    folder_title.config(bg=colors["content_bg"], fg=colors["header_fg"])
    folder_box.config(bg=colors["entry_bg"], highlightbackground=colors["border_color"], highlightcolor=colors["border_color"])
    folder_label.config(bg=colors["entry_bg"], fg=colors["box_fg"])

    buttons_frame.config(bg=colors["content_bg"])
    progress_frame.config(bg=colors["content_bg"])
    progress_label.config(bg=colors["content_bg"], fg=colors["header_fg"])

    # Logs
    logs_top_frame.config(bg=colors["content_bg"])
    logs_title.config(bg=colors["content_bg"], fg=colors["header_fg"])
    logs_subtitle.config(bg=colors["content_bg"], fg=colors["subtext_fg"])
    log_box_frame.config(bg=colors["box_bg"], highlightbackground=colors["border_color"], highlightcolor=colors["border_color"])
    log_box.config(bg=colors["log_bg"], fg=colors["log_fg"], insertbackground=colors["log_fg"])

    # Settings
    settings_header_frame.config(bg=colors["content_bg"])
    settings_header_title.config(bg=colors["content_bg"], fg=colors["header_fg"])
    settings_header_subtitle.config(bg=colors["content_bg"], fg=colors["subtext_fg"])
    settings_boxes_frame.config(bg=colors["content_bg"])

    simple_settings_box.config(bg=colors["box_bg"], highlightbackground=colors["border_color"], highlightcolor=colors["border_color"])
    advanced_settings_box.config(bg=colors["box_bg"], highlightbackground=colors["border_color"], highlightcolor=colors["border_color"])

    simple_settings_title.config(bg=colors["box_bg"], fg=colors["header_fg"])
    advanced_settings_title.config(bg=colors["box_bg"], fg=colors["header_fg"])
    theme_label.config(bg=colors["box_bg"], fg=colors["box_fg"])
    window_mode_label.config(bg=colors["box_bg"], fg=colors["box_fg"])

    for check in [confirm_check, timestamp_check, recursive_check, auto_open_log_check, skip_hidden_check]:
        check.config(
            bg=colors["box_bg"],
            fg=colors["box_fg"],
            activebackground=colors["box_bg"],
            activeforeground=colors["box_fg"],
            selectcolor=colors["box_bg"]
        )

    # Buttons
    browse_btn.config(bg=colors["primary_btn"], fg="white", activebackground=colors["primary_btn_hover"], activeforeground="white")
    organize_btn.config(bg=colors["success_btn"], fg="white", activebackground=colors["success_btn_hover"], activeforeground="white")
    reset_btn.config(bg=colors["neutral_btn"], fg=colors["header_fg"], activebackground=colors["neutral_btn_hover"], activeforeground=colors["header_fg"])
    clear_log_btn.config(bg=colors["danger_btn"], fg="white", activebackground=colors["danger_btn_hover"], activeforeground="white")
    go_to_logs_btn.config(bg=colors["primary_btn"], fg="white", activebackground=colors["primary_btn_hover"], activeforeground="white")

    safe_button_hover(browse_btn, colors["primary_btn"], colors["primary_btn_hover"], "white")
    safe_button_hover(organize_btn, colors["success_btn"], colors["success_btn_hover"], "white")
    safe_button_hover(reset_btn, colors["neutral_btn"], colors["neutral_btn_hover"], colors["header_fg"])
    safe_button_hover(clear_log_btn, colors["danger_btn"], colors["danger_btn_hover"], "white")
    safe_button_hover(go_to_logs_btn, colors["primary_btn"], colors["primary_btn_hover"], "white")

    style.configure(
        "Modern.Horizontal.TProgressbar",
        troughcolor=colors["progress_trough"],
        background=colors["progress_bar"],
        bordercolor=colors["progress_trough"],
        lightcolor=colors["progress_bar"],
        darkcolor=colors["progress_bar"],
        thickness=14
    )

    style.configure(
        "TCombobox",
        fieldbackground=colors["entry_bg"],
        background=colors["entry_bg"],
        foreground=colors["box_fg"]
    )

    update_sidebar_buttons()


def on_theme_change(event=None):
    """Theme dropdown handler."""
    settings_data["theme"] = theme_var.get()
    apply_theme()


def on_window_mode_change(event=None):
    """Window mode dropdown handler."""
    settings_data["window_mode"] = window_mode_var.get()
    apply_window_mode()


# ------------------------------------------------------------
# Folder functions
# ------------------------------------------------------------
def browse_folder():
    """Open folder picker."""
    global selected_folder

    if is_processing:
        return

    folder = filedialog.askdirectory(title="Select Folder to Organize")

    if folder:
        selected_folder = folder
        folder_path_var.set(truncate_path(folder))
        organize_btn.config(state="normal")
        update_status("Folder selected")
        log_message(f"Selected folder: {folder}")


def reset_app():
    """Reset app state."""
    global selected_folder, total_files, organized_files, skipped_files

    if is_processing:
        messagebox.showinfo("Busy", "Please wait until organizing is finished.")
        return

    selected_folder = ""
    total_files = 0
    organized_files = 0
    skipped_files = 0

    folder_path_var.set("No folder selected")
    progress_var.set(0)
    organize_btn.config(state="disabled")
    update_stats()

    log_box.delete("1.0", tk.END)
    log_message("Application reset.")
    update_status("Ready")


def clear_logs():
    """Clear log box."""
    if is_processing:
        messagebox.showinfo("Busy", "Please wait until organizing is finished.")
        return

    log_box.delete("1.0", tk.END)
    log_message("Log cleared.")


# ------------------------------------------------------------
# Organizing logic
# ------------------------------------------------------------
def start_organizing():
    """Start organize process in another thread."""
    if not selected_folder:
        messagebox.showwarning("Warning", "Please select a folder first.")
        return

    if is_processing:
        return

    if settings_data["confirm_before_organizing"]:
        confirm = messagebox.askyesno(
            "Confirm Organization",
            "This will move files into category folders inside the selected folder.\n\n"
            "No files will be deleted.\n\n"
            "Do you want to continue?"
        )
        if not confirm:
            return

    worker = threading.Thread(target=organize_files, daemon=True)
    worker.start()


def collect_files_for_organizing(base_folder):
    """Collect files using current settings."""
    files_to_process = []

    if settings_data["recursive_scan"]:
        for folder_path, folder_names, file_names in os.walk(base_folder):
            folder_names[:] = [
                name for name in folder_names
                if name not in list(FILE_CATEGORIES.keys()) + ["Others"]
            ]

            for file_name in file_names:
                if settings_data["skip_hidden_files"] and is_hidden_file(file_name):
                    continue

                full_path = os.path.join(folder_path, file_name)
                files_to_process.append(full_path)
    else:
        for item in os.listdir(base_folder):
            full_path = os.path.join(base_folder, item)

            if os.path.isfile(full_path):
                if settings_data["skip_hidden_files"] and is_hidden_file(item):
                    continue
                files_to_process.append(full_path)
            else:
                root.after(0, lambda name=item: log_message(f"Skipped folder: {name}"))

    return files_to_process


def organize_files():
    """Main file organizing function."""
    global total_files, organized_files, skipped_files, is_processing

    is_processing = True

    root.after(0, lambda: organize_btn.config(state="disabled"))
    root.after(0, lambda: browse_btn.config(state="disabled"))
    root.after(0, lambda: reset_btn.config(state="disabled"))
    root.after(0, lambda: progress_var.set(0))
    root.after(0, lambda: update_status("Processing..."))

    total_files = 0
    organized_files = 0
    skipped_files = 0

    root.after(0, update_stats)
    root.after(0, lambda: log_message("Started organizing files..."))

    try:
        files = collect_files_for_organizing(selected_folder)
        total_files = len(files)
        root.after(0, update_stats)

        if total_files == 0:
            root.after(0, lambda: update_status("No files found"))
            root.after(0, lambda: log_message("No files found to organize."))
            root.after(0, lambda: messagebox.showinfo("Done", "No files found to organize."))
            return

        for index, source_path in enumerate(files, start=1):
            try:
                file_name = os.path.basename(source_path)
                parent_folder_name = os.path.basename(os.path.dirname(source_path))

                if parent_folder_name in list(FILE_CATEGORIES.keys()) + ["Others"]:
                    skipped_files += 1
                    root.after(0, lambda f=file_name: log_message(f"Skipped already organized file: {f}"))
                else:
                    destination_folder = get_destination_folder(file_name, selected_folder)
                    os.makedirs(destination_folder, exist_ok=True)

                    new_file_name = get_unique_filename(destination_folder, file_name)
                    destination_path = os.path.join(destination_folder, new_file_name)

                    if os.path.abspath(source_path) != os.path.abspath(destination_path):
                        shutil.move(source_path, destination_path)
                        organized_files += 1

                        category_name = os.path.basename(destination_folder)
                        if new_file_name != file_name:
                            root.after(
                                0,
                                lambda old=file_name, new=new_file_name, cat=category_name:
                                log_message(f"Moved {old} -> {cat} as {new}")
                            )
                        else:
                            root.after(
                                0,
                                lambda f=file_name, cat=category_name:
                                log_message(f"Moved {f} -> {cat}")
                            )
                    else:
                        skipped_files += 1
                        root.after(0, lambda f=file_name: log_message(f"Skipped {f}"))

            except Exception as e:
                skipped_files += 1
                root.after(
                    0,
                    lambda f=os.path.basename(source_path), err=str(e):
                    log_message(f"Skipped {f} | Error: {err}")
                )

            progress_percent = (index / total_files) * 100
            root.after(0, lambda p=progress_percent: progress_var.set(p))
            root.after(0, update_stats)

        root.after(0, lambda: update_status("Completed"))
        root.after(0, lambda: log_message("Organizing completed successfully."))

        if settings_data["auto_open_log"]:
            root.after(0, lambda: show_page("Logs"))

        root.after(
            0,
            lambda: messagebox.showinfo(
                "Success",
                f"Organizing completed.\n\n"
                f"Total Files: {total_files}\n"
                f"Organized Files: {organized_files}\n"
                f"Skipped Files: {skipped_files}"
            )
        )

    except Exception as e:
        root.after(0, lambda: update_status("Error occurred"))
        root.after(0, lambda: log_message(f"Error: {e}"))
        root.after(0, lambda: messagebox.showerror("Error", f"Something went wrong:\n{e}"))

    finally:
        is_processing = False
        root.after(0, lambda: browse_btn.config(state="normal"))
        root.after(0, lambda: reset_btn.config(state="normal"))
        root.after(0, lambda: organize_btn.config(state="normal" if selected_folder else "disabled"))


# ------------------------------------------------------------
# Create window
# ------------------------------------------------------------
root = tk.Tk()
root.title("Auto File Organizer")
center_window(root, 1160, 730)
root.minsize(980, 640)

# Keep normal system title bar
# Do NOT use overrideredirect

# Tk variables
folder_path_var = tk.StringVar(value="No folder selected")
status_var = tk.StringVar(value="Ready")
progress_var = tk.DoubleVar(value=0)

total_files_var = tk.StringVar(value="0")
organized_files_var = tk.StringVar(value="0")
skipped_files_var = tk.StringVar(value="0")
home_status_var = tk.StringVar(value="Ready")

page_title_var = tk.StringVar(value="Welcome Back")
page_subtitle_var = tk.StringVar(value="Manage and organize your files safely with a clean desktop interface.")

theme_var = tk.StringVar(value=settings_data["theme"])
window_mode_var = tk.StringVar(value=settings_data["window_mode"])

confirm_var = tk.BooleanVar(value=settings_data["confirm_before_organizing"])
timestamp_var = tk.BooleanVar(value=settings_data["log_timestamps"])
recursive_var = tk.BooleanVar(value=settings_data["recursive_scan"])
auto_open_log_var = tk.BooleanVar(value=settings_data["auto_open_log"])
skip_hidden_var = tk.BooleanVar(value=settings_data["skip_hidden_files"])

# ttk style
style = ttk.Style()
style.theme_use("clam")

# ------------------------------------------------------------
# Main layout
# ------------------------------------------------------------
main_container = tk.Frame(root)
main_container.pack(fill="both", expand=True)

sidebar = tk.Frame(main_container, width=220)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

content_area = tk.Frame(main_container)
content_area.pack(side="right", fill="both", expand=True)

# Sidebar header
app_name_label = tk.Label(
    sidebar,
    text="Auto File\nOrganizer",
    font=("Segoe UI", 20, "bold"),
    justify="left"
)
app_name_label.pack(anchor="w", padx=20, pady=(24, 14))

menu_title_label = tk.Label(
    sidebar,
    text="Navigation",
    font=("Segoe UI", 10, "bold")
)
menu_title_label.pack(anchor="w", padx=20, pady=(0, 10))


def create_sidebar_button(parent, text, command):
    """Create sidebar navigation button."""
    button = tk.Button(
        parent,
        text=text,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        bd=0,
        anchor="w",
        padx=16,
        pady=13,
        command=command
    )
    button.pack(fill="x", padx=12, pady=4)
    return button


btn_home = create_sidebar_button(sidebar, "⌂  Home", lambda: show_page("Home"))
btn_organize = create_sidebar_button(sidebar, "⇄  Organize", lambda: show_page("Organize"))
btn_logs = create_sidebar_button(sidebar, "☰  Logs", lambda: show_page("Logs"))
btn_settings = create_sidebar_button(sidebar, "⚙  Settings", lambda: show_page("Settings"))

sidebar_note_label = tk.Label(
    sidebar,
    text="Safe file sorting\nfor your folders.\nFiles are moved only.",
    font=("Segoe UI", 10),
    justify="left"
)
sidebar_note_label.pack(anchor="w", padx=20, pady=(30, 0))

# Content header
header_frame = tk.Frame(content_area)
header_frame.pack(fill="x", padx=26, pady=(22, 12))

page_title_label = tk.Label(
    header_frame,
    textvariable=page_title_var,
    font=("Segoe UI", 24, "bold")
)
page_title_label.pack(anchor="w")

page_subtitle_label = tk.Label(
    header_frame,
    textvariable=page_subtitle_var,
    font=("Segoe UI", 10)
)
page_subtitle_label.pack(anchor="w", pady=(4, 0))

# Page container
page_container = tk.Frame(content_area)
page_container.pack(fill="both", expand=True, padx=26, pady=(0, 18))

# ------------------------------------------------------------
# HOME PAGE
# ------------------------------------------------------------
home_page = tk.Frame(page_container)

home_top_frame = tk.Frame(home_page)
home_top_frame.pack(fill="x", pady=(0, 18))

home_welcome_title = tk.Label(
    home_top_frame,
    text="Welcome to Auto File Organizer",
    font=("Segoe UI", 17, "bold")
)
home_welcome_title.pack(anchor="w")

home_welcome_subtitle = tk.Label(
    home_top_frame,
    text="A safe and simple desktop tool to sort files into clean category folders.",
    font=("Segoe UI", 10)
)
home_welcome_subtitle.pack(anchor="w", pady=(5, 0))

home_cards_frame = tk.Frame(home_page)
home_cards_frame.pack(fill="x", pady=(0, 18))

total_card = tk.Frame(home_cards_frame, padx=18, pady=18, highlightthickness=1)
total_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

organized_card = tk.Frame(home_cards_frame, padx=18, pady=18, highlightthickness=1)
organized_card.pack(side="left", fill="both", expand=True, padx=8)

skipped_card = tk.Frame(home_cards_frame, padx=18, pady=18, highlightthickness=1)
skipped_card.pack(side="left", fill="both", expand=True, padx=(8, 0))

total_value_label = tk.Label(total_card, textvariable=total_files_var, font=("Segoe UI", 24, "bold"))
total_value_label.pack(anchor="w")
total_title_label = tk.Label(total_card, text="Total Files", font=("Segoe UI", 10))
total_title_label.pack(anchor="w", pady=(8, 0))

organized_value_label = tk.Label(organized_card, textvariable=organized_files_var, font=("Segoe UI", 24, "bold"))
organized_value_label.pack(anchor="w")
organized_title_label = tk.Label(organized_card, text="Organized Files", font=("Segoe UI", 10))
organized_title_label.pack(anchor="w", pady=(8, 0))

skipped_value_label = tk.Label(skipped_card, textvariable=skipped_files_var, font=("Segoe UI", 24, "bold"))
skipped_value_label.pack(anchor="w")
skipped_title_label = tk.Label(skipped_card, text="Skipped Files", font=("Segoe UI", 10))
skipped_title_label.pack(anchor="w", pady=(8, 0))

home_status_box = tk.Frame(home_page, padx=18, pady=18, highlightthickness=1)
home_status_box.pack(fill="x")

home_status_title = tk.Label(home_status_box, text="Current App Status", font=("Segoe UI", 12, "bold"))
home_status_title.pack(anchor="w")

home_status_label = tk.Label(home_status_box, textvariable=home_status_var, font=("Segoe UI", 10))
home_status_label.pack(anchor="w", pady=(8, 0))

go_to_logs_btn = tk.Button(
    home_page,
    text="☰  Open Logs",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    bd=0,
    padx=16,
    pady=11,
    command=lambda: show_page("Logs")
)
go_to_logs_btn.pack(anchor="w", pady=(16, 0))

# ------------------------------------------------------------
# ORGANIZE PAGE
# ------------------------------------------------------------
organize_page = tk.Frame(page_container)

organize_info_box = tk.Frame(organize_page, padx=18, pady=16, highlightthickness=1)
organize_info_box.pack(fill="x", pady=(0, 16))

organize_info_title = tk.Label(
    organize_info_box,
    text="Organizing Information",
    font=("Segoe UI", 12, "bold")
)
organize_info_title.pack(anchor="w")

organize_info_text = tk.Label(
    organize_info_box,
    text="Supported categories: Images, Videos, Documents, Audio, Archives, Programs, and Others.\n"
         "Files are moved safely. Duplicate names are auto-renamed. No files are deleted.",
    font=("Segoe UI", 10),
    justify="left"
)
organize_info_text.pack(anchor="w", pady=(6, 0))

folder_frame = tk.Frame(organize_page)
folder_frame.pack(fill="x", pady=(0, 12))

folder_title = tk.Label(
    folder_frame,
    text="Selected Folder",
    font=("Segoe UI", 11, "bold")
)
folder_title.pack(anchor="w", pady=(0, 6))

folder_box = tk.Frame(folder_frame, highlightthickness=1)
folder_box.pack(fill="x")

folder_label = tk.Label(
    folder_box,
    textvariable=folder_path_var,
    font=("Segoe UI", 10),
    anchor="w",
    padx=12,
    pady=13
)
folder_label.pack(fill="x")

buttons_frame = tk.Frame(organize_page)
buttons_frame.pack(fill="x", pady=(6, 16))

browse_btn = tk.Button(
    buttons_frame,
    text="📁  Browse Folder",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    bd=0,
    padx=16,
    pady=11,
    command=browse_folder
)
browse_btn.pack(side="left", padx=(0, 10))

organize_btn = tk.Button(
    buttons_frame,
    text="▶  Start Organizing",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    bd=0,
    padx=16,
    pady=11,
    state="disabled",
    command=start_organizing
)
organize_btn.pack(side="left", padx=(0, 10))

reset_btn = tk.Button(
    buttons_frame,
    text="↺  Reset",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    bd=0,
    padx=16,
    pady=11,
    command=reset_app
)
reset_btn.pack(side="left")

progress_frame = tk.Frame(organize_page)
progress_frame.pack(fill="x", pady=(0, 14))

progress_label = tk.Label(
    progress_frame,
    text="Progress",
    font=("Segoe UI", 11, "bold")
)
progress_label.pack(anchor="w", pady=(0, 6))

progress_bar = ttk.Progressbar(
    progress_frame,
    style="Modern.Horizontal.TProgressbar",
    variable=progress_var,
    maximum=100
)
progress_bar.pack(fill="x")

# ------------------------------------------------------------
# LOGS PAGE
# ------------------------------------------------------------
logs_page = tk.Frame(page_container)

logs_top_frame = tk.Frame(logs_page)
logs_top_frame.pack(fill="x", pady=(0, 10))

logs_title = tk.Label(
    logs_top_frame,
    text="Full Activity Log",
    font=("Segoe UI", 14, "bold")
)
logs_title.pack(anchor="w")

logs_subtitle = tk.Label(
    logs_top_frame,
    text="This page shows moved files, skipped items, completion notices, and errors.",
    font=("Segoe UI", 10)
)
logs_subtitle.pack(anchor="w", pady=(4, 0))

clear_log_btn = tk.Button(
    logs_page,
    text="🗑  Clear Logs",
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    bd=0,
    padx=16,
    pady=11,
    command=clear_logs
)
clear_log_btn.pack(anchor="w", pady=(0, 10))

log_box_frame = tk.Frame(logs_page, highlightthickness=1)
log_box_frame.pack(fill="both", expand=True)

scrollbar = tk.Scrollbar(log_box_frame)
scrollbar.pack(side="right", fill="y")

log_box = tk.Text(
    log_box_frame,
    font=("Consolas", 10),
    wrap="word",
    yscrollcommand=scrollbar.set,
    relief="flat",
    bd=0,
    padx=12,
    pady=12
)
log_box.pack(fill="both", expand=True)
scrollbar.config(command=log_box.yview)

# ------------------------------------------------------------
# SETTINGS PAGE
# ------------------------------------------------------------
settings_page = tk.Frame(page_container)

settings_header_frame = tk.Frame(settings_page)
settings_header_frame.pack(fill="x", pady=(0, 16))

settings_header_title = tk.Label(
    settings_header_frame,
    text="Application Settings",
    font=("Segoe UI", 14, "bold")
)
settings_header_title.pack(anchor="w")

settings_header_subtitle = tk.Label(
    settings_header_frame,
    text="Choose how the organizer looks and behaves.",
    font=("Segoe UI", 10)
)
settings_header_subtitle.pack(anchor="w", pady=(4, 0))

settings_boxes_frame = tk.Frame(settings_page)
settings_boxes_frame.pack(fill="both", expand=True)

simple_settings_box = tk.Frame(settings_boxes_frame, padx=18, pady=18, highlightthickness=1)
simple_settings_box.pack(side="left", fill="both", expand=True, padx=(0, 8))

advanced_settings_box = tk.Frame(settings_boxes_frame, padx=18, pady=18, highlightthickness=1)
advanced_settings_box.pack(side="left", fill="both", expand=True, padx=(8, 0))

simple_settings_title = tk.Label(simple_settings_box, text="Simple Settings", font=("Segoe UI", 12, "bold"))
simple_settings_title.pack(anchor="w", pady=(0, 12))

theme_label = tk.Label(simple_settings_box, text="Theme", font=("Segoe UI", 10, "bold"))
theme_label.pack(anchor="w", pady=(0, 5))

theme_combo = ttk.Combobox(
    simple_settings_box,
    textvariable=theme_var,
    values=["Default", "Light", "Dark"],
    state="readonly"
)
theme_combo.pack(fill="x", pady=(0, 12))
theme_combo.bind("<<ComboboxSelected>>", on_theme_change)

confirm_check = tk.Checkbutton(
    simple_settings_box,
    text="Enable confirmation popup before organizing",
    variable=confirm_var,
    font=("Segoe UI", 10),
    command=lambda: settings_data.update({"confirm_before_organizing": confirm_var.get()})
)
confirm_check.pack(anchor="w", pady=4)

timestamp_check = tk.Checkbutton(
    simple_settings_box,
    text="Enable activity log timestamps",
    variable=timestamp_var,
    font=("Segoe UI", 10),
    command=lambda: settings_data.update({"log_timestamps": timestamp_var.get()})
)
timestamp_check.pack(anchor="w", pady=4)

advanced_settings_title = tk.Label(advanced_settings_box, text="Advanced Settings", font=("Segoe UI", 12, "bold"))
advanced_settings_title.pack(anchor="w", pady=(0, 12))

recursive_check = tk.Checkbutton(
    advanced_settings_box,
    text="Enable recursive scan for subfolders",
    variable=recursive_var,
    font=("Segoe UI", 10),
    command=lambda: settings_data.update({"recursive_scan": recursive_var.get()})
)
recursive_check.pack(anchor="w", pady=4)

auto_open_log_check = tk.Checkbutton(
    advanced_settings_box,
    text="Enable auto-open log after completion",
    variable=auto_open_log_var,
    font=("Segoe UI", 10),
    command=lambda: settings_data.update({"auto_open_log": auto_open_log_var.get()})
)
auto_open_log_check.pack(anchor="w", pady=4)

skip_hidden_check = tk.Checkbutton(
    advanced_settings_box,
    text="Enable skip hidden files",
    variable=skip_hidden_var,
    font=("Segoe UI", 10),
    command=lambda: settings_data.update({"skip_hidden_files": skip_hidden_var.get()})
)
skip_hidden_check.pack(anchor="w", pady=4)

window_mode_label = tk.Label(advanced_settings_box, text="Window Size Mode", font=("Segoe UI", 10, "bold"))
window_mode_label.pack(anchor="w", pady=(14, 5))

window_mode_combo = ttk.Combobox(
    advanced_settings_box,
    textvariable=window_mode_var,
    values=["Fixed", "Resizable"],
    state="readonly"
)
window_mode_combo.pack(fill="x")
window_mode_combo.bind("<<ComboboxSelected>>", on_window_mode_change)

# ------------------------------------------------------------
# Status bar
# ------------------------------------------------------------
status_bar = tk.Label(
    root,
    textvariable=status_var,
    bd=0,
    relief="flat",
    anchor="w",
    padx=12,
    pady=8,
    font=("Segoe UI", 9)
)
status_bar.pack(side="bottom", fill="x")

# ------------------------------------------------------------
# Start app
# ------------------------------------------------------------
apply_window_mode()
apply_theme()
show_page("Home")
log_message("Application started.")
update_status("Ready")

root.mainloop()