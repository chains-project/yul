use super::{Family, Platform};

/// Returns a description of the current WebAssembly platform.
#[must_use]
pub const fn current() -> Platform {
    Platform {
        family: Family::Wasm,
        os: std::env::consts::OS,
        path_separator: '/',
        line_ending: "\n",
    }
}
