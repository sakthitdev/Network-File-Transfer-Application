# SPS (Sender-Receiver File Transfer Application)

This Python-based application provides a graphical interface for sending and receiving files over TCP. It features file chunking, progress tracking, checksum verification, and a theme switcher for day/night modes. 

## Features

- **File Transfer Modes**: Switch between `Sender` and `Receiver` modes.
- **File Chunking**: Files are split into 4 KB chunks during transfer.
- **Checksum Verification**: Verifies file integrity after transfer using SHA-256 hashing.
- **Night/Day Mode**: Toggle between night and day modes for visual comfort.
- **Graphical User Interface**: Built using `Tkinter` for an intuitive interface.
- **Progress Tracking**: A progress bar shows real-time file transfer status.
- **Multi-threading**: Allows the GUI to remain responsive while file transfers occur in the background.
- **Temporary Chunk Storage**: Chunks of the file are temporarily saved and deleted after transfer.

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.x
- Tkinter (usually bundled with Python)
- PIL (Python Imaging Library) for handling the logo image
- `ttk` for enhanced widgets like the progress bar

## Installation

1. Clone the repository or download the script.
2. Install the required dependencies by running:

```bash
pip install pillow
pip install tk
pip install socket
pip install threading
