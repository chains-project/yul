use super::{Family, Platform};

/// Returns a description of the current Windows platform.
#[must_use]
pub const fn current() -> Platform {
    Platform {
        family: Family::Windows,
        os: std::env::consts::OS,
        path_separator: '\\',
        line_ending: "\r\n",
    }
}
