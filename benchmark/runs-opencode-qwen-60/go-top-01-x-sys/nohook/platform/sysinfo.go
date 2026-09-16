package platform

import "fmt"

// SysInfo returns a human-readable string describing the system and platform.
func SysInfo() (string, error) {
	arch, err := Arch()
	if err != nil {
		return "", err
	}
	version, err := OSVersion()
	if err != nil {
		return "", err
	}
	return fmt.Sprintf("Platform: %s\nArchitecture: %s\nOS Version: %s", OS(), arch, version), nil
}