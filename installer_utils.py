import subprocess
from pathlib import Path
from tqdm import tqdm

def get_app_dir():
    """Get the standard app directory in LocalAppData."""
    app_dir = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / "Vocynx"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

def get_shortcut_paths():
    """Get paths for Desktop and Start Menu shortcuts."""
    desktop = Path(os.environ.get('USERPROFILE')) / "Desktop"
    start_menu = Path(os.environ.get('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    return desktop, start_menu

def create_shortcut(target_path, shortcut_name, desktop=True, start_menu=True):
    """
    Creates Windows shortcuts using PowerShell.
    Zero external dependencies (like pywin32) required.
    """
    try:
        desktop_dir, start_menu_dir = get_shortcut_paths()
        targets = []
        if desktop: targets.append(desktop_dir)
        if start_menu: targets.append(start_menu_dir)

        for folder in targets:
            if not folder.exists():
                folder.mkdir(parents=True, exist_ok=True)
            
            shortcut_path = folder / f"{shortcut_name}.lnk"
            
            # PowerShell command to create a shortcut
            ps_script = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "{target_path}"
            $Shortcut.WorkingDirectory = "{Path(target_path).parent}"
            $Shortcut.Save()
            """
            
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"Failed to create shortcut: {e}")
        return False

def register_startup(app_path):
    """Add the application to Windows startup registry."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Vocynx", 0, winreg.REG_SZ, f'"{app_path}"')
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Failed to register startup: {e}")
        return False

def unregister_startup():
    """Remove the application from Windows startup registry."""
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "Vocynx")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return True # Already removed
    except Exception as e:
        print(f"Failed to unregister startup: {e}")
        return False

def download_model(model_name, target_dir, progress_callback=None):
    """
    Downloads a Whisper model. 
    Note: faster-whisper usually downloads models automatically to ~/.cache/huggingface.
    We want to cache them in the app folder.
    """
    # For a real production app, we would ideally use a direct download link if available,
    # or use the huggingface-hub library to download to a specific path.
    # Since faster-whisper is built on top of CTranslate2/HuggingFace, we can use 
    # the 'download_root' parameter in WhisperModel, but that happens at runtime.
    # For the installer, we'll simulate a download or use a direct URL if we have one.
    
    # Placeholder for actual model download logic if we want to show a progress bar
    # and not just rely on faster-whisper's internal download.
    pass

def install_files(source_dir, target_dir):
    """Copies application files to the target directory."""
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # In a real scenario, we might want to exclude certain files like .git, __pycache__, etc.
        for item in os.listdir(source_dir):
            s = os.path.join(source_dir, item)
            d = os.path.join(target_dir, item)
            if os.path.isdir(s):
                if item not in ['.git', '__pycache__', 'venv', '.gemini', 'packaging']:
                    shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        return True
    except Exception as e:
        print(f"Installation failed: {e}")
        return False
