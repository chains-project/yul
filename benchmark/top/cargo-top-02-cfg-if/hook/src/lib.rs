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
    if #[cfg(target_pointer_width = "64")] {
        pub const POINTER_WIDTH: usize = 64;
    } else {
        pub const POINTER_WIDTH: usize = 32;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn platform_name_is_known() {
        assert_ne!(platform_name(), "unknown");
    }

    #[test]
    fn pointer_width_is_sane() {
        assert!(POINTER_WIDTH == 32 || POINTER_WIDTH == 64);
    }
}
