package backend

import (
	"fmt"

	"golang.org/x/sys/windows/registry"
)

const (
	UninstallKeyPath = `Software\Microsoft\Windows\CurrentVersion\Uninstall\Vocynx`
	RunKeyPath       = `Software\Microsoft\Windows\CurrentVersion\Run`
)

// RegisterApp registers the application in the Windows "Add/Remove Programs" list.
func RegisterApp(displayName, version, publisher, installLoc, iconPath, uninstallStr string) error {
	k, _, err := registry.CreateKey(registry.LOCAL_MACHINE, UninstallKeyPath, registry.ALL_ACCESS)
	if err != nil {
		return fmt.Errorf("failed to create uninstall registry key: %w", err)
	}
	defer k.Close()

	entries := map[string]string{
		"DisplayName":     displayName,
		"DisplayVersion":  version,
		"Publisher":       publisher,
		"InstallLocation": installLoc,
		"UninstallString": uninstallStr,
		"DisplayIcon":     iconPath,
		"NoModify":        "", // signal — handled separately as DWORD
		"NoRepair":        "",
	}

	for key, val := range entries {
		if val == "" {
			continue
		}
		if err := k.SetStringValue(key, val); err != nil {
			return fmt.Errorf("failed to set %s: %w", key, err)
		}
	}

	// Mark as non-modifiable/non-repairable
	_ = k.SetDWordValue("NoModify", 1)
	_ = k.SetDWordValue("NoRepair", 1)

	return nil
}

// SetAutoStart adds or removes the application from the Windows startup (Run) key.
func SetAutoStart(enable bool, appPath string) error {
	k, err := registry.OpenKey(registry.CURRENT_USER, RunKeyPath, registry.ALL_ACCESS)
	if err != nil {
		return fmt.Errorf("failed to open Run registry key: %w", err)
	}
	defer k.Close()

	if enable {
		if err := k.SetStringValue("Vocynx", `"`+appPath+`" --minimized`); err != nil {
			return err
		}
	} else {
		_ = k.DeleteValue("Vocynx")
	}

	return nil
}
