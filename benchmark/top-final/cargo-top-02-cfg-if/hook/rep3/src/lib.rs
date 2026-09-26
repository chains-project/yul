use cfg_if::cfg_if;

cfg_if! {
    if #[cfg(target_os = "linux")] {
        pub fn platform_name() -> &'static str {
            "linux"
        }
    } else if #[cfg(target_os = "macos")] {
        pub fn platform_name() -> &'static str {
            "macos"
        }
    } else if #[cfg(target_os = "windows")] {
        pub fn platform_name() -> &'static str {
            "windows"
        }
    } else {
        pub fn platform_name() -> &'static str {
            "unknown"
        }
    }
}

cfg_if! {
    if #[cfg(unix)] {
        pub fn path_separator() -> char {
            '/'
        }
    } else if #[cfg(windows)] {
        pub fn path_separator() -> char {
            '\\'
        }
    } else {
        pub fn path_separator() -> char {
            '/'
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn platform_name_is_nonempty() {
        assert!(!platform_name().is_empty());
    }

    #[test]
    fn path_separator_is_slash_or_backslash() {
        assert!(path_separator() == '/' || path_separator() == '\\');
    }
}
