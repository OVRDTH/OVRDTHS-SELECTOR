from cx_Freeze import setup, Executable
import sys

build_exe_options = {
    "packages": ["os", "sys", "shutil", "tkinter", "PIL", "webbrowser"],
    "includes": ["tkinter", "tkinter.messagebox", "tkinter.ttk", "PIL.ImageTk", "PIL.Image"],
    "include_files": [
        "README.txt",
        "License.txt",
        ("Resources", "resources"),
        ("Pooled_saves", "pooled_saves"),
    ],
    "excludes": [],
    "optimize": 2,
    "include_msvcr": True, 
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],

}

base = None
if sys.platform == "win32":
    base = "Win32GUI" 

target = Executable(
    script="OVRDTH_SELECTOR.py",
    base=base,
    icon="Resources/icon.ico",
    target_name="OVRDTH_SELECTOR.exe",
)

setup(
    name="OVRDTH_SELECTOR",
    version="1.2.7",
    description="OVRDTH's Selector Application",
    options={"build_exe": build_exe_options},
    executables=[target],
)
