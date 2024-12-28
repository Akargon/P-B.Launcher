import tkinter as tk
import tkinter
from tkinter import ttk
import minecraft_launcher_lib
import subprocess
from threading import Thread
import urllib.request
import os, shutil
import zipfile

variablesurl = "https://www.dropbox.com/scl/fi/xw9igl5r3x3vkm8ihfzog/variables.txt?rlkey=c7yfxyvojnlgmekyv12mlakip&dl=1"
urllib.request.urlretrieve(variablesurl, 'variables.txt')

with open('variables.txt') as file:
    lines = file.readlines()
    modpackurl = lines[0].strip()
    modLoader = lines[1].strip()
    modpackVersion = lines[2].strip()
    vanillaModpackVersion = lines[3].strip()

# Get latest version
latest_version = minecraft_launcher_lib.utils.get_latest_version()["release"]

# Get Minecraft directory
default_minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
modpackFolder = default_minecraft_directory + 'Pibes'
modpackFile = modpackFolder + '\\modpack.zip'
modsPath = modpackFolder + "\\mods"
java = modpackFolder + "\\runtime\\bin\\java.exe"
#minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(latest_version, default_minecraft_directory, default_options)
versionlist = [version['id'] for version in minecraft_launcher_lib.utils.get_available_versions(default_minecraft_directory) if version['type'] == "release"]

settings_file = 'launcher_settings.txt' 
def save_settings(): 
    with open(settings_file, 'w') as file: 
        file.write(f"{usernameinput.get()}\n") 
        file.write(f"{versioncombobox.get()}\n") 
def load_settings(): 
    if os.path.exists(settings_file): 
        with open(settings_file, 'r') as file: 
            lines = file.readlines() 
            if len(lines) >= 2: 
                usernameinput.insert(0, lines[0].strip()) 
                versioncombobox.set(lines[1].strip()) 


def maximum(max_value, value):
    max_value[0] = value
    
def updatemc(version, directory):

    progress_window = tk.Toplevel(root)
    progress_window.title("Updating...")
    progress_window.geometry('300x100')
    progress_window.resizable(0,0)

    progresstext = tk.StringVar()
    progress = tk.IntVar()
    progress_text = tk.Label(progress_window, textvariable=progresstext)
    progress_text.pack(pady=10)
    progress_bar = ttk.Progressbar(progress_window, variable=progress, length=260,  )
    progress_bar.place(relx=0.5, rely=0.5, anchor='center')
    
    max_value = [0]

    callback = {
        "setStatus": lambda text: progresstext.set(text),
        "setProgress": lambda value: progress.set(value),
        "setMax": lambda value: progress_bar.configure(maximum(max_value, value))

    } 
    try:
        # Run the installation in a separate thread to keep the GUI responsive
        Thread(target=lambda: install_minecraft(version, directory, callback, progress_window)).start()
        
    except Exception as e:
        tkinter.messagebox.showerror("Error", f"An error occurred during installation: {str(e)}")

def install_minecraft(version, directory, callback, progress_window):
    try:
        subprocess.run(minecraft_launcher_lib.install.install_minecraft_version(version, directory, callback=callback))
    finally:
        progress_window.destroy()

def playmc(version, directory, user):
    new_options = {
    'username': user,  # Default username
    'uuid': 'offline-mode-uuid',  # Placeholder UUID
    'token': 'offline-mode-token',  # Placeholder token
    'jvmArguments': ['-Xmx8G', '-Xms4G'], #Ram 
    }
    subprocess.run(minecraft_launcher_lib.command.get_minecraft_command(version, directory, new_options))


def installFabric():
    version = "fabric-loader-0.12.12"
    try:
        subprocess.run(minecraft_launcher_lib.fabric.install_fabric_loader(version, modpackFolder))
    except Exception as e:
        tkinter.messagebox.showerror("Error", f"An error occurred during Fabric installation: {str(e)}")

def installForge():
    subprocess.run(java + " -jar " + modpackFolder + "\\forge.jar --installClient " + modpackFolder)
def modpackdownload(popupmodpack) :
    if not os.path.exists(modpackFolder):
        os.makedirs(modpackFolder)
    minecraft_launcher_lib.install.install_minecraft_version(vanillaModpackVersion, modpackFolder)
    urllib.request.urlretrieve(modpackurl, modpackFile)
    with zipfile.ZipFile(modpackFile, 'r') as zip_ref: # Extract all the contents 
        zip_ref.extractall(modpackFolder)
    if  modLoader == 'Fabric' :
        installFabric()
    elif modLoader == 'Forge' :
        # Forge installation goes here
        installForge()
    elif modLoader == 'NeoForge' :
        # NeoForge installation goes here
        pass
    else :
        tkinter.messagebox.showerror("Error", f"An rror occurred during installation: Modloader not found")
    popupmodpack.destroy()  # Close the popup after the download starts    
    

def modpackdownloadpopup():   
    popupmodpack = tkinter.Toplevel()
    popupmodpack.title("Download Modpack")
    popupmodpack.geometry('400x200')
    popupmodpack.resizable(1,1)
    popupmodpacklabel = tkinter.Label(
    popupmodpack, 
    text="You Sure?")
    popupmodpacklabel.pack(pady=10)
    
    button_frame = tk.Frame(popupmodpack) 
    button_frame.pack(pady=10, fill='x')
    download_button = tkinter.Button(button_frame, text="Download", command=lambda: modpackdownload(popupmodpack))
    download_button.pack(side='left', padx=10)
    cancel_button = tkinter.Button(button_frame, text="Cancel", command=lambda: popupmodpack.destroy())
    cancel_button.pack(side='right', padx=10)

def modpackplay(user, xmx=4, xms=8) :
    new_options = {
    'username': user,  # Default username
    'uuid': 'offline-mode-uuid',  # Placeholder UUID
    'token': 'offline-mode-token',  # Placeholder token
    'jvmArguments': ['-Xmx8G', '-Xms4G'], #Ram 
    }
    subprocess.run(minecraft_launcher_lib.command.get_minecraft_command(modpackVersion, modpackFolder, new_options))
    

root = tkinter.Tk()
root.title("PibeLauncher")
root.geometry('500x500')
root.resizable(1,1)

username_label = tkinter.Label(root, text="Username:")
username_label.pack()
usernameinput = tkinter.Entry(root)
usernameinput.pack(pady=10)

version_label = tkinter.Label(root, text="Version:")
version_label.pack()
versioncombobox = ttk.Combobox(root, width=17)
versioncombobox['values'] = versionlist
versioncombobox.set(latest_version)
versioncombobox.pack(pady=10)

vanilla_frame = ttk.Frame(root)
vanilla_frame.pack(pady=10)
updatebutton = tkinter.Button(vanilla_frame, text="Update", command=lambda:updatemc(versioncombobox.get(), default_minecraft_directory))
updatebutton.pack(side='left', padx=10)
playbutton = tkinter.Button(vanilla_frame, text="Play", command=lambda:playmc(versioncombobox.get(), default_minecraft_directory, usernameinput.get()))
playbutton.pack(side='right', padx=10)

modpack_frame = ttk.Frame(root)
modpack_frame.pack(pady=10)
ModpackInstallButton =tk.Button(modpack_frame, text="Modpack Install", command=lambda:modpackdownloadpopup())
ModpackInstallButton.pack(side='left', padx=10)
ModpackPlayButton =tk.Button(modpack_frame, text="Modpack Play", command=lambda:modpackplay(usernameinput.get()))
ModpackPlayButton.pack(side='right', padx=10)

root.protocol("WM_DELETE_WINDOW", lambda: (save_settings(), root.destroy()))
load_settings()
root.mainloop()

