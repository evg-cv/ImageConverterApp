# ImageConvertApp

## Overview
This project is to developing the desktop application to convert png image to cmyk image, while resizing with the actual size, adding spot color channel and 
zooming in & out. The main library for image processing is OpenCV, and the library for application GUI is kivy.
Finally, this project is converted to windows application with exe format.

## Structure

- kivysrc

    The main source code for GUI

- utils

    The source code for image processing
    
- app

    The main execution file
    
- requirements

    All the dependencies for this project
    
- settings

    Several settings including some constants and GUI configuration
    
## Installation

- Environment

    Ubuntu 18.04, Windows 10, Python 3.6
    
- Dependency Installation

    Please navigate to this project directory and run the following command in the terminal.
    
    ```
        pip3 install -r requirements.txt
        python3 -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew --extra-index-url https://kivy.org/downloads/packages/simple/
        python3 -m pip install kivy
        pip3 install pyenchant
    ```

## Execution

- Please run the following command.

    ```
        python3 app.py
    ```
