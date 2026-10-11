package syscallx

type Info struct {
	UptimeSeconds uint64
	TotalMemory   uint64
	FreeMemory    uint64
	Load1         float64
}
