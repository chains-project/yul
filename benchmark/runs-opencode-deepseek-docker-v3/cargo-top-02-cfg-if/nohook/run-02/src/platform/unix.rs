use super::{Family, Platform};

/// Returns a description of the current Unix-like platform.
#[must_use]
pub const fn current() -> Platform {
    Platform {
        family: Family::Unix,
        os: std::env::consts::OS,
        path_separator: '/',
        line_ending: "\n",
    }
}
