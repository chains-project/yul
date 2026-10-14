//! Used for targets with no dedicated backend (e.g. bare-metal or exotic OSes).

use crate::OsFamily;

pub const LINE_ENDING: &str = "\n";

pub fn os_family() -> OsFamily {
    OsFamily::Unknown
}

pub fn config_dir_env() -> Option<&'static str> {
    None
}
