// Package platform gathers OS and kernel details using low-level system calls
// that are not exposed by the Go standard library.
//
// The public API is defined here. Query is implemented once per operating
// system in files with matching build constraints (platform_linux.go,
// platform_darwin.go, platform_windows.go). Consumers only ever import this
// package and call Query.
package platform

// Info describes the running operating system and kernel.
type Info struct {
	OS      string `json:"os"`
	Release string `json:"release"`
	Machine string `json:"machine"`
	Extra   string `json:"extra,omitempty"`
}
