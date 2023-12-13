# Seleccionar el driver de acuerdo al sistema operativo
import os
import platform

def find_chromedriver_in_windows(start_dir="C:/"):
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file == "chromedriver.exe":
                return os.path.join(root, file)
    return None

def select_chromedriver():
    os_name = platform.system()
    if os_name == "Windows":
        # First, try getting the path from environment variable
        chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
        if not chromedriver_path:
            # If not found, search in the common location
            chromedriver_path = find_chromedriver_in_windows()
            if not chromedriver_path:
                # If still not found, prompt the user or use a default path
                chromedriver_path = "C:/chromedriver.exe"
                
    elif os_name == "Linux":
        chromedriver_path = "/usr/local/bin/chromedriver"
        
    return chromedriver_path
