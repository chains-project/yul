package debugprint

// Config controls how the printer renders values.
type Config struct {
	// Indent is emitted once per nesting level. Defaults to two spaces.
	Indent string
	// MaxDepth limits how deep the printer recurses. Zero means unlimited.
	MaxDepth int
	// SortMapKeys sorts map keys so output is deterministic across runs.
	SortMapKeys bool
	// PrintType prefixes composite values with their Go type name.
	PrintType bool
}

// NewDefaultConfig returns the configuration used by the package-level
// helpers.
func NewDefaultConfig() *Config {
	return &Config{
		Indent:      "  ",
		MaxDepth:    0,
		SortMapKeys: true,
		PrintType:   true,
	}
}
