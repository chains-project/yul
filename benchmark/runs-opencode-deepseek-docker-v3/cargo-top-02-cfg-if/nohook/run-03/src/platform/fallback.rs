//! Conservative behaviour for targets that are neither Unix, Windows, nor
//! WebAssembly.
//!
//! Keeping a real implementation here means the crate keeps compiling on
//! exotic targets instead of failing with a "no module" error, and it gives
//! downstream users a place to point at when adding support.

pub(crate) const PATH_SEPARATOR: char = '/';
pub(crate) const PATH_LIST_SEPARATOR: char = ':';
pub(crate) const EXE_SUFFIX: &str = "";
pub(crate) const SHARED_LIBRARY_PREFIX: &str = "";
pub(crate) const SHARED_LIBRARY_SUFFIX: &str = ".bin";
pub(crate) const LINE_ENDING: &str = "\n";
