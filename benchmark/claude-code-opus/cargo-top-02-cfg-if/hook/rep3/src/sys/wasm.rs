use crate::OsFamily;

pub const LINE_ENDING: &str = "\n";

pub fn os_family() -> OsFamily {
    OsFamily::Wasm
}

pub fn config_dir_env() -> Option<&'static str> {
    None
}
