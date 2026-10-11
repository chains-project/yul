//! Behaviour for Unix-family targets (Linux, macOS, the BSDs, Android, iOS).

use cfg_if::cfg_if;

pub(crate) const PATH_SEPARATOR: char = '/';
pub(crate) const PATH_LIST_SEPARATOR: char = ':';
pub(crate) const EXE_SUFFIX: &str = "";
pub(crate) const SHARED_LIBRARY_PREFIX: &str = "lib";
pub(crate) const LINE_ENDING: &str = "\n";

cfg_if! {
    if #[cfg(any(target_os = "macos", target_os = "ios"))] {
        pub(crate) const SHARED_LIBRARY_SUFFIX: &str = ".dylib";
    } else {
        pub(crate) const SHARED_LIBRARY_SUFFIX: &str = ".so";
    }
}
