//! Values shared by every Unix-like target.
//!
//! The platform modules re-export these, so a change here reaches Linux,
//! macOS, and the BSDs at once.

pub(crate) const PATH_SEPARATOR: char = '/';
pub(crate) const PATH_LIST_SEPARATOR: char = ':';
pub(crate) const LINE_ENDING: &str = "\n";
pub(crate) const EXECUTABLE_SUFFIX: &str = "";
