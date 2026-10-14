use crate::OsFamily;

pub const LINE_ENDING: &str = "\r\n";

pub fn os_family() -> OsFamily {
    OsFamily::Windows
}

pub fn config_dir_env() -> Option<&'static str> {
    Some("APPDATA")
}
