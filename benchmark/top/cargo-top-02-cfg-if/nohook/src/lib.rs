use cfg_if::cfg_if;

/// Returns a short label identifying the target platform this crate was built for.
pub fn platform_name() -> &'static str {
    cfg_if! {
        if #[cfg(target_os = "windows")] {
            "windows"
        } else if #[cfg(target_os = "macos")] {
            "macos"
        } else if #[cfg(target_os = "linux")] {
            "linux"
        } else if #[cfg(target_family = "wasm")] {
            "wasm"
        } else {
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

pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }

    #[test]
    fn platform_name_is_known() {
        assert!(!platform_name().is_empty());
    }
}
