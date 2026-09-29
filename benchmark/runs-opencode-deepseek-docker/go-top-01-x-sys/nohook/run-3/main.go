// Command syscli is a small cross-platform CLI that demonstrates calling
// low-level system calls which are not exposed by the Go standard library.
package main

import (
	"flag"
	"fmt"
	"os"

	"example.com/syscli/internal/disk"
)

func main() {
	path := flag.String("path", ".", "filesystem path to inspect")
	human := flag.Bool("human", false, "print sizes in human-readable units")
	flag.Parse()

	total, free, err := disk.Free(*path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "syscli: %v\n", err)
		os.Exit(1)
	}
	used := total - free

	if *human {
		fmt.Printf("path %s: total %s, used %s, free %s\n",
			*path, humanize(total), humanize(used), humanize(free))
		return
	}
	fmt.Printf("path %s: total=%d used=%d free=%d bytes\n", *path, total, used, free)
}

func humanize(n uint64) string {
	const unit = 1024
	if n < unit {
		return fmt.Sprintf("%d B", n)
	}
	div, exp := uint64(unit), 0
	for m := n / unit; m >= unit; m /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f %ciB", float64(n)/float64(div), "KMGTPE"[exp])
}
