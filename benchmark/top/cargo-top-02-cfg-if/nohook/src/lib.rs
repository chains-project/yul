use cfg_if::cfg_if;

pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

cfg_if! {
    if #[cfg(target_os = "windows")] {
        pub fn platform_name() -> &'static str {
            "windows"
        }
    } else if #[cfg(target_os = "macos")] {
        pub fn platform_name() -> &'static str {
            "macos"
        }
    } else if #[cfg(target_os = "linux")] {
        pub fn platform_name() -> &'static str {
            "linux"
        }
    } else {
        pub fn platform_name() -> &'static str {
            "unknown"
        }
    }
}

cfg_if! {
    if #[cfg(target_pointer_width = "64")] {
        pub type Word = u64;
    } else {
        pub type Word = u32;
    }
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
