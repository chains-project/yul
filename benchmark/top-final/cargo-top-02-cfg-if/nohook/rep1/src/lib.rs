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
    } else if #[cfg(target_arch = "wasm32")] {
        pub fn platform_name() -> &'static str {
            "wasm32"
        }
    } else {
        pub fn platform_name() -> &'static str {
            "unknown"
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn returns_a_known_platform_name() {
        assert!(!platform_name().is_empty());
    }
}
