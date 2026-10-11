use crate::{Family, Platform};

pub(crate) const PLATFORM: Platform = Platform::Wasm;
pub(crate) const FAMILY: Family = Family::Wasm;
pub(crate) const PATH_SEPARATOR: char = '/';
pub(crate) const PATH_LIST_SEPARATOR: char = ':';
pub(crate) const LINE_ENDING: &str = "\n";
pub(crate) const EXECUTABLE_SUFFIX: &str = ".wasm";
