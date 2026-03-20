import os
import subprocess
import sys
import shutil
from pathlib import Path

def build_app():
    print("--- Building Vocynx Application ---")
    # Build the main app using the spec file
    # This will create dist/vocynx/vocynx.exe (or similar depending on spec)
    subprocess.run(["pyinstaller", "--noconfirm", "packaging/build.spec"], check=True)
    print("App build complete.")

def build_installer():
    print("\n--- Building Vocynx Installer ---")
    # Build the installer as a single-file EXE
    # --onefile: bundle everything into one EXE
    # --windowed: no console window
    # --icon: use the app icon if available
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "VocynxInstaller",
        "--add-data", f"installer_utils.py{os.pathsep}.",
        "installer.py"
    ]
    
    # Add icon if it exists
    icon_path = Path("vocynx_icon.png")
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
        
    subprocess.run(cmd, check=True)
    print("Installer build complete.")

if __name__ == "__main__":
    try:
        # Check if pyinstaller is installed
        import PyInstaller
    except ImportError:
        print("Error: PyInstaller is not installed. Run 'pip install pyinstaller' first.")
        sys.exit(1)

    # Ensure we are in the project root
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)

    # Create directories if they don't exist
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        print(f"Cleaning old build artifacts in {dist_dir}...")
        # Optional: shutil.rmtree(dist_dir) 
    
    build_app()
    
    # Report app size
    app_exe = dist_dir / "vocynx.exe"
    if app_exe.exists():
        size_mb = app_exe.stat().st_size / (1024 * 1024)
        print(f"\nSUCCESS: Optimized app size: {size_mb:.2f} MB")
        if size_mb > 20:
            print("Warning: Size is still above 20MB target. Further manual library pruning may be needed.")
    
    # build_installer()

    print("\nBuild process finished successfully!")
    print(f"Executables are located in: {dist_dir}")
