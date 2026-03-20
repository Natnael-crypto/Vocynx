package backend

import (
	"context"
	_ "embed"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// Embedded application assets — bundled at compile time.
//
//go:embed assets/vocynx.exe
var embeddedExe []byte

//go:embed assets/vocynx_icon.ico
var embeddedIcon []byte

type Installer struct {
	ctx          context.Context
	logger       *InstallerLogger
	installPath  string
	autoStart    bool
	isInstalling bool
	isFinished   bool
	progress     int
	status       string
	stepTitle    string
	errorMsg     string
}

type InstallOptions struct {
	Path      string `json:"path"`
	AutoStart bool   `json:"autoStart"`
}

func NewInstaller() *Installer {
	return &Installer{
		installPath: `C:\Program Files\Vocynx`,
		status:      "Idle",
		stepTitle:   "Ready to Install",
	}
}

func (i *Installer) SetContext(ctx context.Context) {
	i.ctx = ctx
}

func (i *Installer) CheckAdmin() bool {
	return IsAdmin()
}

func (i *Installer) GetDefaultPath() string {
	return `C:\Program Files\Vocynx`
}

func (i *Installer) StartInstallation(opts InstallOptions) {
	if i.isInstalling {
		return
	}
	i.isInstalling = true
	i.installPath = opts.Path
	i.autoStart = opts.AutoStart

	go i.runInstallation()
}

func (i *Installer) runInstallation() {
	defer func() {
		i.isInstalling = false
		if i.logger != nil {
			i.logger.Close()
		}
	}()

	// 1. Setup logger
	logger, err := NewLogger(i.installPath)
	if err != nil {
		i.reportError(fmt.Sprintf("Failed to initialize logger: %v", err))
		return
	}
	i.logger = logger
	i.logger.Log("Starting Vocynx installation...")

	// 2. Create installation directory
	i.updateProgress(10, "Preparing", "Creating installation directory...")
	if err := EnsureDir(i.installPath); err != nil {
		i.reportError(fmt.Sprintf("Failed to create installation directory: %v", err))
		return
	}
	i.logger.Log(fmt.Sprintf("Created directory: %s", i.installPath))

	// 3. Extract vocynx.exe from embedded data
	i.updateProgress(30, "Copying Files", "Extracting vocynx.exe...")
	exeDst := filepath.Join(i.installPath, "vocynx.exe")
	if err := writeEmbeddedFile(embeddedExe, exeDst, 0755); err != nil {
		i.reportError(fmt.Sprintf("Failed to extract application: %v", err))
		return
	}
	i.logger.Log(fmt.Sprintf("Extracted vocynx.exe → %s", exeDst))

	// 4. Extract icon
	i.updateProgress(50, "Copying Files", "Extracting application icon...")
	iconDst := filepath.Join(i.installPath, "vocynx_icon.ico")
	if err := writeEmbeddedFile(embeddedIcon, iconDst, 0644); err != nil {
		i.logger.Log(fmt.Sprintf("Warning: failed to extract icon: %v", err))
		// Non-fatal — continue
	} else {
		i.logger.Log(fmt.Sprintf("Extracted icon → %s", iconDst))
	}

	// 5. Create shortcuts
	i.updateProgress(65, "Creating Shortcuts", "Creating Desktop & Start Menu shortcuts...")
	desktopLnk := filepath.Join(GetDesktopPath(), "Vocynx.lnk")
	startMenuLnk := filepath.Join(GetStartMenuPath(), "Vocynx.lnk")

	i.logger.Log("Creating Desktop shortcut")
	if err := CreateShortcut(exeDst, desktopLnk, "Vocynx — AI Transcription", iconDst); err != nil {
		i.logger.Log(fmt.Sprintf("Desktop shortcut error: %v", err))
	}

	i.logger.Log("Creating Start Menu shortcut")
	if err := CreateShortcut(exeDst, startMenuLnk, "Vocynx — AI Transcription", iconDst); err != nil {
		i.logger.Log(fmt.Sprintf("Start Menu shortcut error: %v", err))
	}

	// 6. Register in Add/Remove Programs
	i.updateProgress(80, "Registering", "Writing registry entries...")
	uninstallStr := fmt.Sprintf(`"%s" --uninstall`, exeDst)
	if err := RegisterApp("Vocynx", "1.0.0", "Natnael-crypto", i.installPath, iconDst, uninstallStr); err != nil {
		i.logger.Log(fmt.Sprintf("Registry error: %v", err))
	} else {
		i.logger.Log("Registered in Add/Remove Programs")
	}

	// 7. Auto-start (Run registry key)
	if i.autoStart {
		i.updateProgress(92, "Finalizing", "Configuring startup entry...")
		if err := SetAutoStart(true, exeDst); err != nil {
			i.logger.Log(fmt.Sprintf("AutoStart error: %v", err))
		} else {
			i.logger.Log("Startup entry registered")
		}
	}

	// 8. Done
	i.updateProgress(100, "Complete", "Vocynx has been installed successfully.")
	i.isFinished = true
	i.logger.Log("Installation finished successfully.")
	runtime.EventsEmit(i.ctx, "installation_finished", true)
}

// writeEmbeddedFile writes embedded byte data to a file on disk.
func writeEmbeddedFile(data []byte, dst string, perm os.FileMode) error {
	if err := os.MkdirAll(filepath.Dir(dst), 0755); err != nil {
		return err
	}
	return os.WriteFile(dst, data, perm)
}

func (i *Installer) updateProgress(progress int, title, status string) {
	i.progress = progress
	i.stepTitle = title
	i.status = status
	runtime.EventsEmit(i.ctx, "progress_update", map[string]interface{}{
		"progress": progress,
		"title":    title,
		"status":   status,
	})
}

func (i *Installer) reportError(msg string) {
	i.errorMsg = msg
	if i.logger != nil {
		i.logger.Log("CRITICAL ERROR: " + msg)
	}
	runtime.EventsEmit(i.ctx, "installation_error", msg)
}

func (i *Installer) LaunchApp() {
	exePath := filepath.Join(i.installPath, "vocynx.exe")
	cmd := exec.Command(exePath)
	if err := cmd.Start(); err != nil {
		fmt.Printf("Failed to launch app: %v\n", err)
	}
	os.Exit(0)
}

func (i *Installer) CloseInstaller() {
	os.Exit(0)
}
