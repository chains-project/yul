use crate::OsFamily;

pub const LINE_ENDING: &str = "\n";

pub fn os_family() -> OsFamily {
    cfg_if::cfg_if! {
        if #[cfg(apple)] {
            OsFamily::Apple
        } else if #[cfg(linux_like)] {
            OsFamily::Linux
        } else if #[cfg(bsd)] {
            OsFamily::Bsd
        } else {
            OsFamily::OtherUnix
        }
    }
}

pub fn config_dir_env() -> Option<&'static str> {
    cfg_if::cfg_if! {
        if #[cfg(apple)] {
            Some("HOME") // ~/Library/Application Support
        } else {
            Some("XDG_CONFIG_HOME")
        }
    }
}
