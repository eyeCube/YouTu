
import pyperclip
import os
import subprocess
import time
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import sys

'''
    Dependencies

    > python 3.10
    > py2exe

    > tkinter
    > pyperclip
    > ffmpeg
    > yt-dlp

'''

start_row_new = 5
row_new = start_row_new
broken = False
show_required = False
lg = os.getlogin()
u = lg

def end():
    root.destroy()
    sys.exit()
def break_loop():
    global broken
    global show_required
    global row_new
    
    row_new = start_row_new
    root.destroy()
    if str(directory_input[0].get()):
        broken = True
    else:
        show_required = True
def addEntry():
    global frame
    global row_new
    global directory_inputter
    if row_new < 20:
        i = row_new - start_row_new
        directory_input.update({i : StringVar(frame, "")})
        ttk.Label(frame, text=f"URL #{i + 1}").grid(column=1, row=row_new)
        entry = ttk.Entry(frame, textvariable = directory_input[i], justify = LEFT, width=64)
        entry.grid(column=3, row=row_new, sticky="NW")
        directory_inputter.update({i : entry})
        row_new += 1
        
        m = Menu(root, tearoff=0)
        def menu_popup(event):
            try:
                m.tk_popup(event.x_root, event.y_root)
            finally:
                m.grab_release()
        def cut(index):
            pyperclip.copy(str(directory_input[index].get()))
            directory_inputter[index].delete(0, END)
        def copy(index):
            pyperclip.copy(str(directory_input[index].get()))
        def paste(index):
            directory_inputter[index].insert(0, pyperclip.paste())
        m.add_command(label="Cut", command=lambda index=i: cut(index))
        m.add_command(label="Copy", command=lambda index=i: copy(index))
        m.add_command(label="Paste", command=lambda index=i: paste(index))
        directory_inputter[i].bind("<Button-3>", menu_popup)
    
def file_dialog():
    global destination
    destination = filedialog.askdirectory(mustexist = True)
    dest_entry.delete(0, END)
    dest_entry.insert(0, destination)
    print(destination)
    
def make_default_destination(user):
    destination = ""
    file_path = "./default.txt"
    if os.path.isfile(file_path):
        with open(file_path, "r") as file:
            for line in file:
                destination = line
    else:
        with open(file_path, "w") as file:
            file.write(f"C:\\Users\\{user}\\Desktop\\YouTube")
            destination = f"C:\\Users\\{user}\\Desktop\\YouTube"
    return destination

def set_default():
    with open("./default.txt", "w") as file:
        file.write(destination)
        ttk.Label(frame, text="Default output folder set to").grid(column=0, row=0)
        ttk.Label(frame, text=f"    {destination}").grid(column=0, row=1)

directory_inputter = {}
destination = ""
first_time = True

while not broken:

    root = Tk()
    frame = ttk.Frame(root, padding=10)
    frame.grid()
    
    directory_input = {0 : StringVar(frame, "")}
    
    user = StringVar(frame, lg).get()
    trying_audio_only = StringVar(frame, "0")

    destination = make_default_destination(user)

    ttk.Label(frame, text="Destination").grid(column=1, row=2)
    dest_entry = ttk.Entry(frame, textvariable = destination, justify = LEFT, width=64)
    dest_entry.grid(column=3, row=2, sticky="NW")
    dest_entry.insert(0, destination)
    ttk.Button(frame, text="Explore...", command=file_dialog).grid(column=2, row=2, sticky="NW")
    ttk.Button(frame, text="Set Default", command=set_default).grid(column=0, row=2, sticky="NW")

    # video combined or audio only
    Radiobutton(
        frame, text = "Video & Audio", variable = trying_audio_only, 
        value = 0, indicator = 1,
        ).grid(column=1, row=3, sticky="NW")
    Radiobutton(
        frame, text = "Audio Only", variable = trying_audio_only, 
        value = 1, indicator = 1,
        ).grid(column=0, row=3)

    #quality
    ttk.Label(frame, text="Quality").grid(column=1, row=4)
    options = ["240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p"]
    quality_selection = StringVar(frame, "")
    quality_selection.set(options[4])
    dropdown = OptionMenu(frame, quality_selection, *options).grid(column=2, row=4)

    if first_time:
        addEntry()
    
    ttk.Button(frame, text="+", command=addEntry).grid(column=2, row=row_new - 1, sticky="NW")
    if show_required:
        ttk.Label(frame, text="At least one URL is required.").grid(column=0, row=0)

    button = ttk.Button(frame, text="Confirm", command=break_loop).grid(column=1, row=300, sticky="NW")

    ttk.Button(frame, text="Cancel", command=end).grid(column=3, row=300, sticky="NW")

    root.mainloop()

# after the window is closed, run the command


success = False
for did, dvar in directory_input.items():
    quality = int(quality_selection.get()[:-1])
    print(f"Using quality: {quality}")
    val = str(dvar.get())
    dr = val.split('&')[0]
    if dr != val:
        print(f"URL: {val} converted to {dr}")
    lg = user
    audio_only = int(trying_audio_only.get())

    if not dr:
        continue

    if not os.path.exists(destination):
        print("Creating YouTube directory.")
        os.mkdir(destination)

    for ti in range(2):
        fba = " -f -ba" if audio_only else ' -f "bv*+ba/b"'
        command = f'"./yt-dlp.exe" -P {destination} -o "%(uploader)s/%(title)s.%(ext)s" -o "subtitle:%(uploader)s/subs/%(title)s.%(ext)s" --merge-output-format mp4 {dr} --write-subs{fba} -S "res:{quality}"'
        print(command)
        
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                )
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                success = True
                print("yt-dlp command executed successfully.")
                print("Output:")
                print(stdout.decode())
            else:
                print(f"yt-dlp command failed with exit code: {process.returncode}")
                print("Error:")
                print(stderr.decode())

        except FileNotFoundError:
            print("Error: yt-dlp command not found. Ensure it's installed and in your PATH.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        if not audio_only: # run two tries with audio-only mode; first with audio-only, second without
            break
        audio_only = False
        if ti == 0:
            print("Retrying with video format (audio-only not available)......")
if not success:
    input("No URL entered. Press ENTER to exit.")

input("Success. Press ENTER to exit.")
