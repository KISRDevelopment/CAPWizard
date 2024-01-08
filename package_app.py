import sys
import subprocess

def package_app():
    app_name = 'CAPWizard'
    tk_logo_path = './Icon/logo.png'  # Default icon path

    # Determine the operating system
    if sys.platform.startswith('darwin'):
        # MacOS
        icon_path = './Icon/MacOS.icns'
        # Note: For MacOS, the separator in --add-data is a colon (:)
        os_command = f'pyinstaller --onefile --windowed --icon={icon_path} --add-data="{tk_logo_path}:Icon" --name={app_name} main.py'
        subprocess.run(os_command, shell=True)
        # Create .dmg file
        dmg_command = f'create-dmg "dist/{app_name}.app" --overwrite'
        subprocess.run(dmg_command, shell=True)
    elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
        # Windows
        icon_path = './Icon/Windows.ico'
        # Note: For Windows, the separator in --add-data is a semicolon (;)
        os_command = f'pyinstaller --onefile --windowed --icon={icon_path} --add-data="{tk_logo_path};Icon" --name={app_name} main.py'
        subprocess.run(os_command, shell=True)
    else:
        print("Unsupported OS")
        return

if __name__ == "__main__":
    package_app()
