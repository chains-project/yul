use super::{Family, Platform};

/// Returns a description of a target with no dedicated platform module.
#[must_use]
pub const fn current() -> Platform {
    Platform {
        family: Family::Other,
        os: std::env::consts::OS,
        path_separator: '/',
        line_ending: "\n",
    }
}
