import socket
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import hashlib
import os
from PIL import Image, ImageTk 

CHUNK_SIZE = 4096  # 4 KB


NIGHT_MODE_COLORS = {
    'background': '#727272',
    'foreground': '#ffffff',
    'highlight': '#47474b',
    'button': '#47474b',
    'button_text': '#ffffff'
}


DAY_MODE_COLORS = {
    'background': '#ffffff',
    'foreground': '#000000',
    'highlight': '#dddddd',
    'button': '#007bff',
    'button_text': '#ffffff'
}

current_mode = 'Day'

def set_mode(mode):
    global current_mode
    if mode == 'Night':
        colors = NIGHT_MODE_COLORS
    else:
        colors = DAY_MODE_COLORS

    
    root.configure(bg=colors['background'])
    mode_label.configure(bg=colors['background'], fg=colors['foreground'])
    file_label.configure(bg=colors['background'], fg=colors['foreground'])
    save_dir_label.configure(bg=colors['background'], fg=colors['foreground'])
    ip_label.configure(bg=colors['background'], fg=colors['foreground'])
    port_label.configure(bg=colors['background'], fg=colors['foreground'])
    console_text.configure(bg=colors['highlight'], fg=colors['foreground'])
    progress_bar.configure(style='TProgressbar')
    
    browse_button.configure(bg=colors['button'], fg=colors['button_text'])
    save_dir_button.configure(bg=colors['button'], fg=colors['button_text'])
    start_button.configure(bg=colors['button'], fg=colors['button_text'])
    
  
    style = ttk.Style()
    style.configure('TProgressbar', background=colors['button'], troughcolor=colors['highlight'])

    current_mode = mode

def select_file():
    file_path = filedialog.askopenfilename()
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)

def select_save_dir():
    dir_path = filedialog.askdirectory()
    save_dir_entry.delete(0, tk.END)
    save_dir_entry.insert(0, dir_path)

def calculate_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            sha256.update(chunk)
    return sha256.hexdigest()

def save_chunk(data, chunk_index, file_name):
    chunk_path = f"{file_name}_chunk{chunk_index}"
    with open(chunk_path, "wb") as f:
        f.write(data)
    return chunk_path

def delete_chunks(file_name, chunk_count):
    for chunk_index in range(chunk_count):
        chunk_path = f"{file_name}_chunk{chunk_index}"
        if os.path.exists(chunk_path):
            os.remove(chunk_path)
            console_text.insert(tk.END, f"Deleted chunk: {chunk_path}\n")
        else:
            console_text.insert(tk.END, f"Chunk {chunk_path} not found for deletion.\n")

def send_file(file_path, ip, port, console_text, progress_bar):
    try:
        file_size = os.path.getsize(file_path)
        file_hash = calculate_hash(file_path)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            console_text.insert(tk.END, f"Connected to {ip}:{port}\n")

           
            s.sendall(file_hash.encode())

            
            chunk_index = 0
            with open(file_path, "rb") as f:
                while chunk := f.read(CHUNK_SIZE):
                    
                    chunk_path = save_chunk(chunk, chunk_index, os.path.basename(file_path))
                    console_text.insert(tk.END, f"Saved chunk: {chunk_path}\n")
                    
                    s.sendall(chunk)
                    chunk_index += 1
                    
                   
                    progress_bar['value'] = (f.tell() / file_size) * 100
                    progress_bar.update()

            console_text.insert(tk.END, "File sent successfully.\n")

            
            delete_chunks(os.path.basename(file_path), chunk_index)

    except Exception as e:
        console_text.insert(tk.END, f"Error during file transfer: {e}\n")

def receive_file(port, save_dir, console_text, progress_bar):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            s.listen(1)
            console_text.insert(tk.END, "Waiting for a connection...\n")
            conn, addr = s.accept()
            with conn:
                console_text.insert(tk.END, f"Connected to {addr}\n")

               
                file_hash = conn.recv(64).decode()

                
                file_path = filedialog.asksaveasfilename(initialdir=save_dir, title="Save File As")
                if not file_path:
                    console_text.insert(tk.END, "No file selected for saving.\n")
                    return

                received_size = 0
                chunk_index = 0

                
                with open(file_path, "wb") as f:
                    while True:
                        data = conn.recv(CHUNK_SIZE)
                        if not data:
                            break
                        
                        
                        f.write(data)
                        received_size += len(data)
                        
                       
                        progress_bar['value'] = (received_size / (received_size or 1)) * 100
                        progress_bar.update()

                console_text.insert(tk.END, "File received and saved successfully.\n")

               
                received_file_hash = calculate_hash(file_path)
                if received_file_hash == file_hash:
                    console_text.insert(tk.END, "Checksum verification passed.\n")
                else:
                    console_text.insert(tk.END, "Checksum verification failed. File might be corrupted.\n")

    except Exception as e:
        console_text.insert(tk.END, f"Error during file reception: {e}\n")

def start_sending():
    file_path = file_entry.get()
    ip = ip_entry.get()
    port = int(port_entry.get())
    if file_path and ip and port:
        console_text.insert(tk.END, f"Sending file {file_path} to {ip}:{port}\n")
        threading.Thread(target=send_file, args=(file_path, ip, port, console_text, progress_bar)).start()
    else:
        messagebox.showwarning("Input Error", "Please provide all necessary inputs.")

def start_receiving():
    port = int(port_entry.get())
    save_dir = save_dir_entry.get()
    if port and save_dir:
        console_text.insert(tk.END, f"Waiting to receive file on port {port}\n")
        threading.Thread(target=receive_file, args=(port, save_dir, console_text, progress_bar)).start()
    else:
        messagebox.showwarning("Input Error", "Please provide all necessary inputs.")

def switch_mode(mode):
    if mode == "Sender":
        file_entry.grid()
        browse_button.grid()
        ip_label.grid()
        ip_entry.grid()
        save_dir_entry.grid_remove()
        save_dir_button.grid_remove()
        start_button.config(text="Start Transfer", command=start_sending)
    elif mode == "Receiver":
        file_entry.grid_remove()
        browse_button.grid_remove()
        ip_label.grid_remove()
        ip_entry.grid_remove()
        save_dir_entry.grid()
        save_dir_button.grid()
        start_button.config(text="Start Reception", command=start_receiving)


root = tk.Tk()
root.title("SPS")


logo_image = Image.open('iconeee.png') 
logo_photo = ImageTk.PhotoImage(logo_image)
root.iconphoto(True, logo_photo)


mode_label = tk.Label(root, text="Select Mode:")
mode_label.grid(row=0, column=0, padx=10, pady=10)
mode_var = tk.StringVar(value="Sender")
sender_radio = tk.Radiobutton(root, text="Sender", variable=mode_var, value="Sender", command=lambda: switch_mode("Sender"))
sender_radio.grid(row=0, column=1, padx=10, pady=10)
receiver_radio = tk.Radiobutton(root, text="Receiver", variable=mode_var, value="Receiver", command=lambda: switch_mode("Receiver"))
receiver_radio.grid(row=0, column=2, padx=10, pady=10)


file_label = tk.Label(root, text="Select File:")
file_label.grid(row=1, column=0, padx=10, pady=10)
file_entry = tk.Entry(root, width=40)
file_entry.grid(row=1, column=1, padx=10, pady=10)
browse_button = tk.Button(root, text="Browse", command=select_file)
browse_button.grid(row=1, column=2, padx=10, pady=10)


save_dir_label = tk.Label(root, text="Save Directory:")
save_dir_label.grid(row=2, column=0, padx=10, pady=10)
save_dir_entry = tk.Entry(root, width=40)
save_dir_entry.grid(row=2, column=1, padx=10, pady=10)
save_dir_button = tk.Button(root, text="Browse", command=select_save_dir)
save_dir_button.grid(row=2, column=2, padx=10, pady=10)


ip_label = tk.Label(root, text="IP Address:")
ip_label.grid(row=3, column=0, padx=10, pady=10)
ip_entry = tk.Entry(root)
ip_entry.grid(row=3, column=1, padx=10, pady=10)

port_label = tk.Label(root, text="Port:")
port_label.grid(row=4, column=0, padx=10, pady=10)
port_entry = tk.Entry(root)
port_entry.grid(row=4, column=1, padx=10, pady=10)


console_text = tk.Text(root, height=10, width=50)
console_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)


progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=6, column=0, columnspan=3, padx=10, pady=10)


start_button = tk.Button(root, text="Start Transfer", command=start_sending)
start_button.grid(row=7, column=0, columnspan=3, pady=10)


night_mode_button = tk.Button(root, text="Switch to Night Mode", command=lambda: set_mode('Night' if current_mode == 'Day' else 'Day'))
night_mode_button.grid(row=8, column=0, columnspan=3, pady=10)


switch_mode("Sender")
set_mode('Day')

root.mainloop()
