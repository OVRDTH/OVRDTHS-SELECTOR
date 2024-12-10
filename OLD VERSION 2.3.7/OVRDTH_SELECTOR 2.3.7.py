import sys
import os


if sys.platform == "win32" and hasattr(sys, "frozen"):
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(os.path.dirname(sys.executable))
    else:
        os.environ["PATH"] = os.path.dirname(sys.executable) + os.pathsep + os.environ["PATH"]

import shutil
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from PIL import Image, ImageTk
import webbrowser


__version__ = '2.3.7' 


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for frozen executables """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def copy_save(selected_save):
    appdata_dir = os.getenv('LOCALAPPDATA')
    game_save_dir = os.path.join(appdata_dir, "VersionTest54", "Saved", "SaveGames")

    if not os.path.exists(game_save_dir):
        messagebox.showerror("Error", f"Game save directory not found: {game_save_dir}")
        return

    pooled_saves_dir = resource_path('pooled_saves')
    selected_save_path = os.path.join(pooled_saves_dir, selected_save)

    try:
        shutil.copytree(selected_save_path, game_save_dir, dirs_exist_ok=True)
        messagebox.showinfo("Success", f"Save '{selected_save}' has been loaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load the save. Error: {e}")

def ask_loadout_name():
    """Create a custom dialog box for asking the loadout name."""
    dialog = tk.Toplevel(root)
    dialog.title("Save Loadout")
    
    if os.path.exists(icon_path):
        img = Image.open(icon_path)
        photo_icon = ImageTk.PhotoImage(img)
        dialog.iconphoto(False, photo_icon)
    
    dialog.configure(bg="#2e2e2e")
    
    label = tk.Label(dialog, text="Enter a name for the loadout:", font=("Arial", 12), fg="#ffffff", bg="#2e2e2e")
    label.pack(padx=20, pady=10)

    loadout_name_entry = tk.Entry(dialog, width=30, bg="#1c1c1c", fg="#ffffff", font=("Arial", 10))
    loadout_name_entry.pack(padx=20, pady=10)
    
    user_input = tk.StringVar()

    def on_ok():
        user_input.set(loadout_name_entry.get())
        dialog.destroy()

    button_frame = tk.Frame(dialog, bg="#2e2e2e")
    button_frame.pack(pady=10)
    
    ok_button = tk.Button(button_frame, text="OK", command=on_ok, 
                          bg="#565656", fg="#ffffff", font=("Arial", 10), relief="groove", cursor="hand2")
    ok_button.pack(side=tk.LEFT, padx=10)
    
    cancel_button = tk.Button(button_frame, text="Cancel", command=dialog.destroy, 
                              bg="#565656", fg="#ffffff", font=("Arial", 10), relief="groove", cursor="hand2")
    cancel_button.pack(side=tk.LEFT, padx=10)

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)
    
    return user_input.get() if user_input.get() else None



def save_loadout():
    appdata_dir = os.getenv('LOCALAPPDATA')
    game_save_dir = os.path.join(appdata_dir, "VersionTest54", "Saved", "SaveGames")

    if not os.path.exists(game_save_dir):
        messagebox.showerror("Error", f"Game save directory not found: {game_save_dir}")
        return

    folder_name = ask_loadout_name()

    if folder_name:
        pooled_saves_dir = resource_path('pooled_saves')
        new_folder_path = os.path.join(pooled_saves_dir, folder_name)

        try:
            os.makedirs(new_folder_path, exist_ok=True)

            files_to_copy = ['SG Player Equipment.sav']

            for filename in files_to_copy:
                source_file = os.path.join(game_save_dir, filename)
                if os.path.exists(source_file):
                    shutil.copy(source_file, new_folder_path)
                else:
                    print(f"File not found: {filename}")

            messagebox.showinfo("Success", f"Loadout '{folder_name}' has been saved successfully!")
            
            load_save_folders()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save the loadout. Error: {e}")


def delete_save():
    selected_index = save_listbox.curselection()
    if selected_index:
        selected_save = save_listbox.get(selected_index)
        pooled_saves_dir = resource_path('pooled_saves')
        save_to_delete = os.path.join(pooled_saves_dir, selected_save)

        confirm = messagebox.askyesno("Delete Loadout", f"Are you sure you want to delete '{selected_save}'?")
        if confirm:
            try:
                shutil.rmtree(save_to_delete)
                messagebox.showinfo("Success", f"Loadout '{selected_save}' has been deleted successfully!")
                load_save_folders()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete the loadout. Error: {e}")

def load_save_folders():
    pooled_saves_dir = resource_path('pooled_saves')

    if not os.path.exists(pooled_saves_dir):
        messagebox.showerror("Error", f"Pooled save directory not found: {pooled_saves_dir}")
        return

    save_folders = [f for f in os.listdir(pooled_saves_dir) if os.path.isdir(os.path.join(pooled_saves_dir, f))]

    if not save_folders:
        messagebox.showinfo("No saves found", "No save files are available in the pooled saves directory.")
        return

    save_listbox.delete(0, tk.END)
    for folder in save_folders:
        save_listbox.insert(tk.END, folder)

def on_folder_double_click(event):
    selected_index = save_listbox.curselection()
    if selected_index:
        selected_save = save_listbox.get(selected_index)
        copy_save(selected_save)

def open_youtube():
    webbrowser.open("https://www.youtube.com/@OVRDTH")  # Replace with your YouTube channel link

def open_readme():
    readme_path = resource_path('README.txt')
    if os.path.exists(readme_path):
        try:
            os.startfile(readme_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open README file: {e}")
    else:
        messagebox.showerror("Error", "README file not found.")

def show_version():
    result = messagebox.askyesno(
        "Version",
        f"OVRDTH'S SELECTOR\nVersion: {__version__}\n\n"
        "Visit my Nexus Mods page or the Google Drive for updates.\n\n"
        "Would you like to open the download page?"
    )
    if result:
        nexus_mods_url = 'https://www.nexusmods.com/halfsword/mods/11?tab=files'
        webbrowser.open(nexus_mods_url)

def remind_to_update():
    result = messagebox.askyesno(
        "Check for Updates",
        "For bug fixes and new loadouts, please check for updates on my Nexus Mods page. (If mod is unpublished, get from Google Drive link)\n\n"
        "Would you like to visit the download page now?"
    )
    if result:
        nexus_mods_url = 'https://www.nexusmods.com/halfsword/mods/11?tab=files' 
        webbrowser.open(nexus_mods_url)

def open_google_drive():
    result = messagebox.askyesno(
        "Google Drive",
        "Would you like to visit the Google Drive for all published versions?"
    )
    if result:
        google_drive_url = 'https://drive.google.com/drive/folders/1gYokPfdgc8mg3J1PhIQqFr-LqcZ1OOh8?usp=sharing' 
        webbrowser.open(google_drive_url)

# GUI Setup
root = tk.Tk()
root.title("OVRDTH'S SELECTOR")
root.geometry("550x650") 

style = ttk.Style()

style.configure("TButton", 
                background="#2e2e2e", 
                foreground="#ffffff", 
                font=("Arial", 10),
                padding=6)

style.map("TButton", 
          background=[("pressed", "#333333"), ("active", "#666666")])


icon_path = resource_path(os.path.join('resources', 'iconexe.ico'))
if os.path.exists(icon_path):
    try:
        img = Image.open(icon_path)
        photo_icon = ImageTk.PhotoImage(img)
        root.iconphoto(False, photo_icon)
    except Exception as e:
        print(f"Failed to set window icon: {e}")
else:
    print(f"Icon not found at: {icon_path}")

root.configure(bg="#2e2e2e")

top_button_frame = tk.Frame(root, bg="#565656")
top_button_frame.pack(pady=10)

readme_button = tk.Button(top_button_frame, text="VIEW README", command=open_readme, 
                          bg="#565656", fg="#ffffff", font=("Arial", 10), relief="groove", cursor="hand2")
readme_button.grid(row=0, column=0, padx=0)

version_button = tk.Button(top_button_frame, text="NEXUS", command=show_version, 
                           bg="#565656", fg="#ffffff", font=("Arial", 10), relief="groove", cursor="hand2")
version_button.grid(row=0, column=1, padx=0)

google_drive_button = tk.Button(top_button_frame, text="GOOGLE DRIVE", command=open_google_drive, 
                                bg="#565656", fg="#ffffff", font=("Arial", 10), relief="groove", cursor="hand2")
google_drive_button.grid(row=0, column=2, padx=0)

header = tk.Label(root, text="SELECT LOADOUT", font=("Arial", 16), fg="#ffffff", bg="#2e2e2e")
header.pack(pady=10)

list_frame = tk.Frame(root, bg="#2e2e2e")
list_frame.pack(pady=10, padx=10, fill="both", expand=True)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

save_listbox = tk.Listbox(
    list_frame, width=50, height=10, yscrollcommand=scrollbar.set,
    bg="#1c1c1c", fg="#ffffff", font=("Arial", 10)
)
save_listbox.pack(side="left", fill="both", expand=True)

scrollbar.config(command=save_listbox.yview)

button_frame = tk.Frame(root, bg="#565656")
button_frame.pack(pady=10)

load_button = tk.Button(button_frame, text="LOAD LOADOUTS", command=load_save_folders, 
                        bg="#565656", fg="#ffffff", font=("Arial", 10), relief="groove", cursor="hand2")
load_button.grid(row=0, column=0, padx=0)

save_button = tk.Button(button_frame, text="SAVE LOADOUT", command=save_loadout, 
                        bg="#565656", fg="#ffffff", font=("Arial", 10), relief="groove", cursor="hand2")
save_button.grid(row=0, column=1, padx=0)

delete_button = tk.Button(button_frame, text="DELETE LOADOUT", command=delete_save, 
                          bg="#565656", fg="#ffffff", font=("Arial", 10), relief="groove", cursor="hand2")
delete_button.grid(row=0, column=2, padx=0)

save_listbox.bind('<Double-1>', on_folder_double_click)

youtube_icon_path = resource_path(os.path.join('resources', 'youtube_icon.png'))

if os.path.exists(youtube_icon_path):
    try:
        youtube_image = Image.open(youtube_icon_path)
        youtube_image = youtube_image.resize((40, 40), Image.LANCZOS)
        youtube_photo = ImageTk.PhotoImage(youtube_image)

        youtube_label = tk.Label(root, image=youtube_photo, bg="#2e2e2e", cursor="hand2")
        youtube_label.pack(pady=10)

        youtube_label.bind("<Button-1>", lambda e: open_youtube())

        youtube_text = tk.Label(
            root, text="Click here for my videos!", font=("Arial", 10),
            fg="#ffffff", bg="#565656", cursor="hand2"
        )
        youtube_text.pack(pady=5)
        youtube_text.bind("<Button-1>", lambda e: open_youtube())
    except Exception as e:
        print(f"Failed to load YouTube icon: {e}")
else:
    youtube_label = tk.Label(
        root, text="Visit my YouTube channel", font=("Arial", 12),
        fg="#ffffff", bg="#565656", cursor="hand2"
    )
    youtube_label.pack(pady=10)
    youtube_label.bind("<Button-1>", lambda e: open_youtube())


version_label = tk.Label(
    root, text=f"Version: {__version__}", font=("Arial", 8), fg="#ffffff", bg="#565656"
)
version_label.pack(side="right", anchor="se", padx=10, pady=10)

remind_to_update()

root.mainloop()
