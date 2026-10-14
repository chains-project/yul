# systool

Cross-platform CLI (Linux, macOS, Windows) using OS-level system calls.

## Layout

    cmd/systool/          CLI entry point
    internal/sysinfo/     example platform-abstracted package
      sysinfo.go          shared API (exported types and functions)
      sysinfo_unix.go     linux || darwin, via golang.org/x/sys/unix
      sysinfo_windows.go  windows, via golang.org/x/sys/windows

## Conventions

- Use `golang.org/x/sys/unix` and `golang.org/x/sys/windows`, not the standard
  `syscall` package. `syscall` is frozen and missing many newer calls and constants.
- Put the shared API in a file with no build tags. Each platform file implements
  an unexported function (`get()` here), so a missing implementation fails at
  compile time.
- For Win32 APIs that x/sys does not wrap, use `windows.NewLazySystemDLL` +
  `NewProc` (see `sysinfo_windows.go`). Don't use `NewLazyDLL`, which is open
  to DLL preloading attacks.
- For Linux/macOS calls missing from x/sys/unix, prefer `unix.Syscall` with a
  `unix.SYS_*` number on Linux. On macOS, raw syscall numbers are not a stable
  ABI, so go through libSystem (cgo or x/sys's own wrappers).

## Verify all targets

    for t in linux/amd64 linux/arm64 darwin/amd64 darwin/arm64 windows/amd64 windows/arm64; do
      GOOS=${t%/*} GOARCH=${t#*/} go vet ./... || echo "FAIL $t"
    done
