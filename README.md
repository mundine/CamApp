# CamApp

## Table of Contents
1. [Introduction](#introduction)
2. [Configuration](#configuration)
   - [Environment Variables](#environment-variables)
   - [Camera Settings](#camera-settings)
   - [Network Configuration](#network-configuration)
   - [Application Configuration](#application-configuration)
3. [Usage](#usage)
   - [Starting the Server](#starting-the-server)
   - [Accessing the Web Interface](#accessing-the-web-interface)
   - [Troubleshooting](#troubleshooting)



## Introduction
CamApp is a web-based application designed to manage and control multiple IP cameras. It provides an interface for real-time video streaming and PTZ (Pan-Tilt-Zoom) control.

The application is built using modern web technologies and follows best practices in software development. It uses WebRTC for video streaming, ensuring efficient, low-latency video feeds.

Key components of CamApp include:

- Multi-camera management
- Real-time video streaming
- PTZ control interface
- Web-based user interface
- Scalable architecture for multiple users and cameras

## Configuration
Instructions on how to configure the application, including:
- Environment variables
- Camera settings
- Network configuration

### Environment Variables
CamApp uses environment variables for camera credentials. There is a `.env` file in the root directory of the project holding these variables.

### Camera Settings
Camera configurations are defined in the `config.py` file. Each camera is configured with the following parameters:

- `user`: Username for camera authentication (loaded from environment variables)
- `password`: Password for camera authentication (loaded from environment variables)
- `ip`: IP address of the camera
- `ptz_port`: Port number for PTZ control
- `rtsp_port`: Port number for RTSP streaming

The current configuration includes the following cameras:

- Central
- West 2
- East 2
- OPF 1
- OPF 2

To modify or add camera configurations, edit the `Cameras` dictionary in `config.py`.

### Network Configuration
Ensure that the server running CamApp has network access to all configured cameras. The application uses the following ports:

- RTSP streaming: Port 554 for all cameras
- PTZ control: Port 80 for all cameras
- Web interface: The application runs on port 5000 by default


### Application Configuration
The main configuration is handled through the `config.py` file, which loads the environment variables and sets up the camera configurations. No additional configuration files are required for basic setup.

For advanced configuration options or to modify the application behavior, you may need to edit the relevant Python files in the project structure.

## Usage

### Starting the Server

1. Ensure all configurations are set correctly in `config.py` and `.env` files.

2. Open a terminal and navigate to the CamApp directory.

3. Run the following command to start the server:

   ```
   python main.py
   ```

   The server will start and listen on `0.0.0.0:5000` by default.

### Accessing the Web Interface

1. Open a web browser and navigate to `http://localhost:5000` (or the appropriate IP address if accessing from another device on the network).

2. You should see the CamApp interface with camera selection buttons on the left side.


### Troubleshooting

- If you encounter connection issues, check the server console & log files located in `/logs/` for error messages.
- If the camera is not visible in the list, check the IP address and credentials in the `.env` file.
- Ensure that the camera IP addresses and credentials in the configuration are correct.


### Key Components:

- `camera/`: Contains classes for camera management and configuration.
- `client/`: Handles client-side operations and data structures.
- `connection/`: Manages connections between clients and cameras.
- `controller/`: Implements camera control logic.
- `rtc/`: Handles WebRTC-related functionality.
- `server/`: Contains the main server application and routing.
- `static/`: Stores static files for the web interface.
  - `js/`: JavaScript files for frontend functionality.
  - `templates/`: HTML templates for the web interface.
- `tests/`: Contains unit tests for various components.
- `utils/`: Utility functions and classes, including logging.
- `config.py`: Central configuration file for the application.
- `main.py`: Entry point of the application.
- `app_state.py`: Manages the overall state of the application.

This structure separates concerns and organizes the codebase into logical modules, making it easier to maintain and extend the application.

