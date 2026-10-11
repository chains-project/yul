/// Broad classification of the current build target.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub enum Family {
    /// Unix-like targets such as Linux, macOS, and the BSDs.
    Unix,
    /// Microsoft Windows targets.
    Windows,
    /// WebAssembly targets, including WASI.
    Wasm,
    /// Any target not covered by the variants above.
    Other,
}

/// A description of the platform this crate was compiled for.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[non_exhaustive]
pub struct Platform {
    /// The target family this description was produced for.
    pub family: Family,
    /// The `target_os` name reported by the toolchain.
    pub os: &'static str,
    /// The character separating components in a path.
    pub path_separator: char,
    /// The sequence that terminates a line in this platform's convention.
    pub line_ending: &'static str,
}
