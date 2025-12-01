import os
import platform
import subprocess

def open_file_manager(path):
    """Opens the default file manager to the specified path."""
    if platform.system() == "Windows":
        # Use os.startfile on Windows
        # f = list(path.split("\\"))
        # print("----------------------",f)
        # _path = input("Enter the folder name: ")
        # path_ = "\\".join(f[f.index(_path):])
        os.startfile(path)
    elif platform.system() == "Darwin":
        # Use 'open' command on macOS
        subprocess.Popen(["open", path])
    else:
        # Assume Linux, use 'xdg-open' command
        subprocess.Popen(["xdg-open", path])

# --- Example Usage ---

# Define the path you want to open. Use raw strings (r"...") on Windows
# to handle backslashes correctly, or use forward slashes for cross-platform compatibility.
# The path below is an example; replace it with your desired path.

path_to_open = r"C:/Program Files (x86)/HP/HPAudioSwitch/Resources" 
f = input("Enter folder name: ")
_path = path_to_open.split("/")

paath = "/".join(_path[:_path.index(f)+1])
# path_ = ""
# for i in _path:
#     if i == f:
#         path_ += i 
#         break
#     else:
#         path_ += i + "/"
print(paath)

# print("----------------------",_path)
# path_to_open = "/home/youruser/Documents/MyProjectFolder" # Example Linux/macOS Path

open_file_manager(paath)