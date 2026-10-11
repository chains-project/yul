//! Behaviour for `wasm32` targets.
//!
//! WebAssembly is handled first in [`super`]'s selection block because a
//! `wasm32-wasip1` build can otherwise be reported as Unix-like.

pub(crate) const PATH_SEPARATOR: char = '/';
pub(crate) const PATH_LIST_SEPARATOR: char = ':';
pub(crate) const EXE_SUFFIX: &str = ".wasm";
pub(crate) const SHARED_LIBRARY_PREFIX: &str = "";
pub(crate) const SHARED_LIBRARY_SUFFIX: &str = ".wasm";
pub(crate) const LINE_ENDING: &str = "\n";
