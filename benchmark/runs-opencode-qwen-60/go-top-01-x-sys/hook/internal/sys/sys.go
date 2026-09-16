package sys

// SystemInfo holds system information gathered from low-level
// platform-specific system calls.
type SystemInfo struct {
	Platform string
	OS       string
	Arch     string
}

// GetInfo returns system information using platform-specific
// low-level system calls.
func GetInfo() (*SystemInfo, error) {
	return getDefaultInfo()
}