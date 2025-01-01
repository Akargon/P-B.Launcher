import tkinter as tk
import tkinter
from tkinter import ttk
import minecraft_launcher_lib
import subprocess
from threading import Thread
import urllib.request
import os, shutil, sys
import zipfile
import psutil


# Function to handle resource paths
def resource_path(relative_path):
    """ Get the absolute path to a resource, works for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Get Minecraft directory
default_minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
launcherFolder = default_minecraft_directory + 'Pibes'
vanillaFolder = launcherFolder + '\\vanilla'
modpackFolder = launcherFolder + '\\modpack'
modpackFile = modpackFolder + '\\modpack.zip'
modsPath = modpackFolder + "\\mods"
java = modpackFolder + "\\runtime\\bin\\java.exe"
variables_file = launcherFolder + '\\variables.txt'
settings_file = launcherFolder + '\\launcher_settings.txt' 
availableRAM = psutil.virtual_memory().total
latest_version = minecraft_launcher_lib.utils.get_latest_version()["release"]
versionlist = [version['id'] for version in minecraft_launcher_lib.utils.get_version_list() if version['type'] == "release"]

if not os.path.exists(launcherFolder):
    os.makedirs(launcherFolder)
variablesurl = "https://www.dropbox.com/scl/fi/xw9igl5r3x3vkm8ihfzog/variables.txt?rlkey=c7yfxyvojnlgmekyv12mlakip&dl=1"
urllib.request.urlretrieve(variablesurl, variables_file)
with open(variables_file) as file:
    lines = file.readlines()
    modpackurl = lines[0].strip()
    modLoader = lines[1].strip()
    modpackVersion = lines[2].strip()
    vanillaModpackVersion = lines[3].strip()
    fabricVersion = lines[4].strip()

def save_settings(): 
    if not os.path.exists(launcherFolder):
        os.makedirs(launcherFolder)
    with open(settings_file, 'w') as file: 
        file.write(f"{usernameinput.get()}\n") 
        file.write(f"{versioncombobox.get()}\n") 
        file.write(f"{maxRamSlide.get()}\n") 
        file.write(f"{seeInstalledVersionsVar.get()}\n") 
def load_settings(): 
    if os.path.exists(settings_file): 
        with open(settings_file, 'r') as file: 
            lines = file.readlines() 
            usernameinput.insert(0, lines[0].strip()) 
            versioncombobox.set(lines[1].strip())
            maxRamSlide.set(lines[2].strip())
            seeInstalledVersionsVar.set(lines[3].strip())

   
def updatemc(version, directory):
    minecraft_launcher_lib.install.install_minecraft_version(version, directory) 

def playmc(version, directory, user, xmx):
    options = {
        'username': user,  # Default username
        'uuid': 'offline-uuid',  # Placeholder UUID
        'token': 'offline-token',  # Placeholder token
        'jvmArguments': [f'-Xmx{xmx}m',  # Ram max memory
                         '-Dminecraft.api.auth.host=https://nope.invalid',
                         '-Dminecraft.api.account.host=https://nope.invalid',
                         '-Dminecraft.api.session.host=https://nope.invalid',
                         '-Dminecraft.api.services.host=https://nope.invalid'],
    }
 
    installedVersionList = [version['id'] for version in minecraft_launcher_lib.utils.get_installed_versions(vanillaFolder)]
    if version in installedVersionList :
        print(f'Running minecraft {version}')
    else :
        print(f'Minecraft {version} not installed, downloading now')
        updatemc(version, directory)
        subprocess.run(minecraft_launcher_lib.command.get_minecraft_command(version, directory, options))

    original_dir = os.getcwd()
    os.chdir(vanillaFolder)
    try:
        subprocess.run(
            minecraft_launcher_lib.command.get_minecraft_command(version, directory, options),
            cwd=vanillaFolder
        )
    finally:
        # Change back to the original directory
        os.chdir(original_dir)
            
def installFabric():
    fabric = modpackFolder + "\\fabric.jar"
    minecraft_launcher_lib.fabric.install_fabric(vanillaModpackVersion, modpackFolder, fabricVersion)
    
def installForge():
    forge = modpackFolder + "\\forge.jar"
    subprocess.run(f'{java} -jar {forge} --installClient {modpackFolder}')
def installNeoForge():
    neoforge = modpackFolder + "\\neoforge.jar"
    subprocess.run(f'{java} -jar {neoforge} --installClient {modpackFolder}')

def modpackdownload(popupmodpack) :
    installedVersionList = [version['id'] for version in minecraft_launcher_lib.utils.get_installed_versions(modpackFolder)]
    if os.path.exists(modpackFolder):
        shutil.rmtree(modpackFolder)
        os.makedirs(modpackFolder)
    else :
        os.makedirs(modpackFolder)
    urllib.request.urlretrieve(modpackurl, modpackFile)
    with zipfile.ZipFile(modpackFile, 'r') as zip_ref: # Extract all the contents 
        zip_ref.extractall(modpackFolder)
    if not vanillaModpackVersion in installedVersionList :
        updatemc(vanillaModpackVersion, modpackFolder)
    if  modLoader == 'Fabric' :
        installFabric()
    elif modLoader == 'Forge' :
        installForge()
    elif modLoader == 'NeoForge' :
        installNeoForge()
    else :
        print("Error", f"An rror occurred during installation: Modloader not found")
    popupmodpack.destroy()  # Close the popup after the download starts    
    

def modpackdownloadpopup():   
    popupmodpack = tkinter.Toplevel()
    popupmodpack.title("Download Modpack")
    popupmodpack.geometry('300x100')
    popupmodpack.resizable(1,1)
    popupmodpacklabel = tkinter.Label(popupmodpack, text="You Sure?")
    popupmodpacklabel.pack(pady=10)
    
    button_frame = tk.Frame(popupmodpack) 
    button_frame.pack(pady=10)
    cancel_button = tkinter.Button(button_frame, text="Cancel", command=lambda: popupmodpack.destroy())
    cancel_button.pack(side='left', padx=10)
    download_button = tkinter.Button(button_frame, text="Download", command=lambda: modpackdownload(popupmodpack))
    download_button.pack(side='left', padx=10)


def modpackplay(user, xmx) :
    options = {
        'username': user,  # Default username
        'uuid': 'offline-uuid',  # Placeholder UUID
        'token': 'offline-token',  # Placeholder token
        'jvmArguments': [f'-Xmx{xmx}m',  # Ram max memory
                         '-Dminecraft.api.auth.host=https://nope.invalid',
                         '-Dminecraft.api.account.host=https://nope.invalid',
                         '-Dminecraft.api.session.host=https://nope.invalid',
                         '-Dminecraft.api.services.host=https://nope.invalid'],
    }
    original_dir = os.getcwd()
    os.chdir(modpackFolder) 
    try:
        subprocess.run(
            minecraft_launcher_lib.command.get_minecraft_command(modpackVersion, modpackFolder, options),
            cwd=modpackFolder
        )
    finally:
        # Change back to the original directory
        os.chdir(original_dir)


def update_versions(*args): 
    if seeInstalledVersionsVar.get(): 
        installedVersionList = [version['id'] for version in minecraft_launcher_lib.utils.get_installed_versions(vanillaFolder)] 
        versioncombobox['values'] = installedVersionList 
    else: 
        versioncombobox['values'] = versionlist 
        versioncombobox.set(latest_version)

root = tk.Tk()
root.title("PibeLauncher")
root.geometry('500x200')
root.resizable(1,1)


icon_image = tk.PhotoImage(file=resource_path('assets\\icon.png'))
root.iconphoto(True, icon_image)

frame = ttk.Frame(root)
frame.pack(pady = 10)
username_label = tkinter.Label(frame, text="Username:")
username_label.pack(side='left', padx=10)
usernameinput = tkinter.Entry(frame)
usernameinput.pack(side='left', padx=10)

seeInstalledVersionsVar = tkinter.BooleanVar()
seeInstalledVersionsVar.set(False)
seeInstalledVersions = tkinter.Checkbutton(frame, text='Installed Versions', variable=seeInstalledVersionsVar)
seeInstalledVersions.pack(side='right', padx=10)
seeInstalledVersionsVar.trace_add('write', update_versions)

versioncombobox = ttk.Combobox(frame, width=17)
versioncombobox.set(latest_version)
versioncombobox.pack(side='right', padx=10)
version_label = tkinter.Label(frame, text="Version:")
version_label.pack(side='right', padx=10)

maxRamSlide = tk.Scale(root, from_=2024, to=availableRAM / (1024 ** 2), orient='horizontal', length=200, showvalue=True, label='Max RAM')
maxRamSlide.pack(pady=10)

buttonsFrame = ttk.Frame(root)
buttonsFrame.pack(pady=10)
ModpackInstallButton =tk.Button(buttonsFrame, text="Modpack Install", command=lambda:modpackdownloadpopup())
ModpackInstallButton.pack(side='left', padx=10)
ModpackPlayButton =tk.Button(buttonsFrame, text="Modpack Play", command=lambda:modpackplay(usernameinput.get(), maxRamSlide.get()))
ModpackPlayButton.pack(side='left', padx=10)
playbutton = tkinter.Button(buttonsFrame, text="Play", command=lambda:playmc(versioncombobox.get(), vanillaFolder, usernameinput.get(), maxRamSlide.get()))
playbutton.pack(side='left', padx=10)

root.protocol("WM_DELETE_WINDOW", lambda: (save_settings(), root.destroy()))
load_settings()
update_versions()
root.mainloop()