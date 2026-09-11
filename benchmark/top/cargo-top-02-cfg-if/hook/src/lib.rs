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
        pub type Word = u64;
    } else {
        pub type Word = u32;
    }
}

pub fn add(left: Word, right: Word) -> Word {
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
    fn reports_a_platform_name() {
        assert!(!platform_name().is_empty());
    }
}
