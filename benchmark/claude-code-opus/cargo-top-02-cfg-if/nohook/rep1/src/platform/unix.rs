//! Generic Unix (BSDs, illumos, etc.) backend.

pub const PLATFORM_NAME: &str = "unix";

pub fn path_separator() -> char {
    '/'
}
