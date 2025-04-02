import tkinter
from ttkthemes import ThemedTk
from tkinter import ttk
import tkinter.messagebox
import minecraft_launcher_lib
import subprocess
import threading
import requests
import os, shutil, sys
import zipfile
import psutil
import wget
import uuid
from urllib.request import urlretrieve

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
variables_file = launcherFolder + '\\variables.txt'
settings_file = launcherFolder + '\\launcher_settings.txt' 
availableRAM = psutil.virtual_memory().total
latest_version = minecraft_launcher_lib.utils.get_latest_version()["release"]

if not 'java-runtime-delta' in minecraft_launcher_lib.runtime.get_installed_jvm_runtimes(launcherFolder):
    minecraft_launcher_lib.runtime.install_jvm_runtime('java-runtime-delta', launcherFolder)
java = minecraft_launcher_lib.runtime.get_executable_path('java-runtime-delta', launcherFolder)

if not os.path.exists(launcherFolder):
    os.makedirs(launcherFolder)
variablesurl = "https://www.dropbox.com/scl/fi/xw9igl5r3x3vkm8ihfzog/variables.txt?rlkey=c7yfxyvojnlgmekyv12mlakip&dl=1"
if os.path.exists(variables_file):
    os.remove(variables_file) # if exist, remove it directly
urlretrieve(variablesurl, variables_file)
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
        file.write(f"{RamSlide.get()}\n") 
        file.write(f"{seeInstalledVersionsVar.get()}\n") 
def load_settings(): 
    update_versions()
    if os.path.exists(settings_file): 
        with open(settings_file, 'r') as file: 
            lines = file.readlines() 
            usernameinput.insert(0, lines[0].strip()) 
            versioncombobox.set(lines[1].strip())
            RamSlide.set(lines[2].strip())
            seeInstalledVersionsVar.set(lines[3].strip())
    else :
        usernameinput.insert(0, 'Player')
        versioncombobox.set(latest_version)
        RamSlide.set(4096)

def install_minecraft(version, directory):
    playButton.config(state=tkinter.DISABLED)
    progressWindow = tkinter.Toplevel()
    progressWindow.title("Downloading minecraft")
    progressWindow.geometry('300x130')
    progressWindow.resizable(0,0)

    progress = ttk.Progressbar(progressWindow, orient='horizontal', length=200, mode='determinate')
    progress.pack(pady=10)
    progress['value'] = 0

    string_var = tkinter.StringVar()
    string_var.set("Downloading Minecraft")
    text = tkinter.Label(progressWindow, textvariable=string_var)
    text.pack(pady=10)

    progressWindow.update_idletasks()

    callback = {
        "setStatus": lambda text: printText(text),
        "setProgress": lambda value: printProgressBar(value),
    }
    
    def printProgressBar(value):
        progress['value'] = value
        progressWindow.update_idletasks()
    def printText(text):
        string_var.set(text)
        progressWindow.update_idletasks()
    def install():
        minecraft_launcher_lib.install.install_minecraft_version(version, directory, callback)
        progressWindow.destroy()
        playButton.config(state=tkinter.NORMAL)
    thread = threading.Thread(target=install)
    thread.start()

def playmc(version, directory, user, xmx, isModpack = False):
    # Check if Minecraft is already running
    # for thread in threading.enumerate():
    #     if thread.name == 'Minecraft':
    #         if not tkinter.messagebox.askyesno(title = 'Minecraft is already running', message = 'Do you wish to continue anyway?') : 
    #             return
    for proc in psutil.process_iter(['pid', 'name']):
        if 'java' in proc.info['name']:
            if tkinter.messagebox.askyesno(title = 'Minecraft is already running', message = 'Do you wish to continue anyway?') : 
                break
            else:
                return

    if not isModpack :
        installedVersionList = [version['id'] for version in minecraft_launcher_lib.utils.get_installed_versions(directory)]
        if not version in installedVersionList:
            install_minecraft(version, directory)
            return
    elif isModpack :
        installedVersionList = [version['id'] for version in minecraft_launcher_lib.utils.get_installed_versions(directory)]
        if not version in installedVersionList:
            tkinter.messagebox.showerror(title = 'Modpack not installed', message = 'Modpack is not installed, please install first.')
            return
        
    def run_minecraft():
        options = {
            'username': user,
            'uuid': str(uuid.uuid4()),
            'token': '',
            'jvmArguments': [f'-Xmx{xmx}m',  # Ram max memory
                            '-Dminecraft.api.auth.host=https://nope.invalid',
                            '-Dminecraft.api.account.host=https://nope.invalid',
                            '-Dminecraft.api.session.host=https://nope.invalid',
                            '-Dminecraft.api.services.host=https://nope.invalid'],
            'executablePath' : java
        }
        # Launch Minecraft
        command = minecraft_launcher_lib.command.get_minecraft_command(version, directory, options)
        subprocess.Popen(command, cwd=directory, creationflags=subprocess.CREATE_NO_WINDOW)

    
    # Run the run_minecraft function in a separate thread
    thread = threading.Thread(target=run_minecraft, name='Minecraft')
    thread.start()

def modpackdownload(popupmodpack):
    popupmodpack.destroy()
    ModpackUpdateButton.config(state=tkinter.DISABLED)
    # Create a progress bar window
    progressWindow = tkinter.Toplevel()
    progressWindow.title("Download Modpack")
    progressWindow.geometry('300x130')
    progressWindow.resizable(0,0)    

    progress = ttk.Progressbar(progressWindow, orient='horizontal', length=200, mode='determinate')
    progress.pack(pady=10)
    progress['value'] = 0

    progress2 = ttk.Progressbar(progressWindow, orient='horizontal', length=200, mode='determinate')
    progress2.pack(pady=10)
    progress2['value'] = 0

    string_var = tkinter.StringVar()
    string_var.set("Downloading modpack")
    text = ttk.Label(progressWindow, textvariable=string_var)
    text.pack(pady=10)


    progressWindow.update_idletasks()

    def installFabric():
        fabric = modpackFolder + "\\fabric.jar"
        subprocess.run(f'{java} -jar {fabric} client -dir {modpackFolder} -noprofile -downloadMinecraft')
        minecraft_launcher_lib.fabric.install_fabric(vanillaModpackVersion, modpackFolder, fabricVersion, java=java, callback=callback)
    def installForge():
        forge = modpackFolder + "\\forge.jar"
        subprocess.run(f'{java} -jar {forge} --installClient {modpackFolder}')
    def installNeoForge():
        neoforge = modpackFolder + "\\neoforge.jar"
        subprocess.run(f'{java} -jar {neoforge} --installClient {modpackFolder}')

    def printProgressBar(value):
        progress2['value'] = value
    def printText(text):
        string_var.set(text)

    callback = {
        "setStatus": lambda text: printText(text),
        "setProgress": lambda value: printProgressBar(value),
    }

    def show_progress(block_num, block_size, total_size):
        progress2['value'] = block_num * block_size / total_size *100
        progressWindow.update_idletasks()

    def update():
        try:
            printText("Clearing modpack folder")
            if os.path.exists(modpackFolder):
                for file in os.listdir(modpackFolder):
                    file_path = os.path.join(modpackFolder, file)
                    if file == "mods" or file == "config":
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except Exception as e:
                            print(e)
            
            # Update progress bar
            progress['value'] = 33
            printText("Downloading update")
            progressWindow.update_idletasks()

            urlretrieve(modpackurl, modpackFile, show_progress)

            # Update progress bar
            progress['value'] = 66
            printText("Extracting update")
            progressWindow.update_idletasks()
            
            with zipfile.ZipFile(modpackFile, 'r') as zip_ref: # Extract all the contents 
                zip_ref.extractall(modpackFolder)
            
            # Update progress bar
            progress['value'] = 100
            printText("Done")
            progressWindow.update_idletasks()

        except FileNotFoundError as e:
            tkinter.messagebox.showerror(title='Error', message=f"File not found: {e}")
        except Exception as e:
            tkinter.messagebox.showerror(title='Error', message=f"An error occurred: {e}")
        finally:
            ModpackUpdateButton.config(state=tkinter.NORMAL)
            update_versions()
            progressWindow.destroy()
            
    def download():
        try:
            printText("Clearing modpack folder")
            if os.path.exists(modpackFolder):
                for file in os.listdir(modpackFolder):
                    file_path = os.path.join(modpackFolder, file)
                    if not file == "saves" :
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except Exception as e:
                            print(e)
            else:
                os.makedirs(modpackFolder)
            
            # Update progress bar
            progress['value'] = 20
            printText("Downloading modpack zip")
            progressWindow.update_idletasks()

            urlretrieve(modpackurl, modpackFile, show_progress)

            # Update progress bar
            progress['value'] = 40
            printText("Extracting modpack")
            progressWindow.update_idletasks()
            
            with zipfile.ZipFile(modpackFile, 'r') as zip_ref: # Extract all the contents 
                zip_ref.extractall(modpackFolder)
            
            # Update progress bar
            progress['value'] = 60
            printText("Downloading Minecraft")
            progressWindow.update_idletasks()
            
            minecraft_launcher_lib.install.install_minecraft_version(vanillaModpackVersion, modpackFolder, callback=callback)
            
            # Update progress bar
            progress['value'] = 80
            printText("Installing Modloader")
            progressWindow.update_idletasks()

            if modLoader == 'Fabric':
                installFabric()
            elif modLoader == 'Forge':
                installForge()
            elif modLoader == 'NeoForge':
                installNeoForge()
            else:
                print("Error", f"An error occurred during installation: Modloader not found")
            
            # Update progress bar
            progress['value'] = 100
            printText("Done")
            progressWindow.update_idletasks()

        except FileNotFoundError as e:
            tkinter.messagebox.showerror(title='Error', message=f"File not found: {e}")
        except Exception as e:
            tkinter.messagebox.showerror(title='Error', message=f"An error occurred: {e}")
        finally:
            ModpackUpdateButton.config(state=tkinter.NORMAL)
            update_versions()
            progressWindow.destroy()

    if modpackVersion in [version['id'] for version in minecraft_launcher_lib.utils.get_installed_versions(modpackFolder)]:
        thread = threading.Thread(target=update)
        thread.start()
    else:
        thread = threading.Thread(target=download)
        thread.start()
    # Run the download function in a separate thread
    
    
def modpackdownloadpopup():   
    popupmodpack = ThemedTk(toplevel=True, theme="adapta", themebg=True)
    popupmodpack.title("Download Modpack")
    popupmodpack.geometry('300x150')
    popupmodpack.resizable(1,1)
    popupmodpacklabel = ttk.Label(popupmodpack, text="This will make a fresh install of the modpack \ndeleting previous saves and configs, \ncontinue anyway?")
    popupmodpacklabel.pack(pady=10)
    
    button_frame = ttk.Frame(popupmodpack) 
    button_frame.pack(pady=10)
    cancel_button = ttk.Button(button_frame, text="Cancel", command=lambda: popupmodpack.destroy())
    cancel_button.pack(side='left', padx=10)
    download_button = ttk.Button(button_frame, text="Download", command=lambda: modpackdownload(popupmodpack))
    download_button.pack(side='left', padx=10)

def update_versions(*args): 
    actualVersion = versioncombobox.get()
    if seeInstalledVersionsVar.get(): 
        installedVersionList = [version['id'] for version in minecraft_launcher_lib.utils.get_installed_versions(vanillaFolder)] 
        if os.path.exists(modpackFolder):
            installedVersionList.insert(0, 'Modpack')
        versioncombobox['values'] = installedVersionList 
        if not actualVersion in installedVersionList: 
            versioncombobox.set(installedVersionList[0])
    else: 
        versionList = [version['id'] for version in minecraft_launcher_lib.utils.get_version_list() if version['type'] == "release"]
        if os.path.exists(modpackFolder):
            versionList.insert(0, 'Modpack')
        versioncombobox['values'] = versionList 

def playCommand() : 
    if versioncombobox.get() == 'Modpack':
        playmc(modpackVersion, modpackFolder, usernameinput.get(), ramint, True)
    else:
        playmc(versioncombobox.get(), vanillaFolder, usernameinput.get(), ramint)

root = ThemedTk(theme="adapta", themebg=True)
root.title("P-B.Launcher")
root.geometry('500x200')
root.resizable(1,1)

icon_image = tkinter.PhotoImage(file=resource_path('assets\\icon.png'))
root.iconphoto(True, icon_image)

frame = ttk.Frame(root)
frame.pack(pady = 10)
username_label = ttk.Label(frame, text="Username:")
username_label.pack(side='left', padx=10)
usernameinput = ttk.Entry(frame)
usernameinput.pack(side='left', padx=10)

seeInstalledVersionsVar = tkinter.BooleanVar()
seeInstalledVersionsVar.set(False)
seeInstalledVersions = ttk.Checkbutton(frame, text='Installed Versions', variable=seeInstalledVersionsVar)
seeInstalledVersions.pack(side='right', padx=10)
seeInstalledVersionsVar.trace_add('write', update_versions)

versioncombobox = ttk.Combobox(frame,state="readonly", height=5, width=10)
versioncombobox.pack(side='right', padx=10)

def update_ramLabel(value): 
    global ramint
    ramint = round(float(value) / 512) * 512
    ramValue.config(text=f"{ramint} MB")

ramFrame = ttk.Frame(root)
ramFrame.pack(pady=10)
ramLabel = ttk.Label(ramFrame, text="Ram:")
ramLabel.pack(padx=10,side='left')
RamSlide = ttk.Scale(ramFrame, from_=2024, to=availableRAM / (1024 ** 2), orient='horizontal', length=200, command=update_ramLabel)
RamSlide.pack(padx=10, side='left')
ramValue = ttk.Label(ramFrame, text=f"2024 MB")
ramValue.pack(padx=10,side='left')

buttonsFrame = ttk.Frame(root)
buttonsFrame.pack(pady=10)
ModpackUpdateButton =ttk.Button(buttonsFrame, text="Update modpack", command=lambda:modpackdownloadpopup())
ModpackUpdateButton.pack(side='left', padx=10)
playButton = ttk.Button(buttonsFrame, text="Play", command=lambda:playCommand())
playButton.pack(side='left', padx=10)

root.protocol("WM_DELETE_WINDOW", lambda: (save_settings(), root.destroy()))
load_settings()
root.mainloop()