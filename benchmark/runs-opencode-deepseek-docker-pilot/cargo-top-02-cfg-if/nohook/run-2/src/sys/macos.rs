use super::Platform;
use crate::Family;

/// macOS backend.
pub(crate) struct Imp;

impl Platform for Imp {
    const NAME: &'static str = "macos";
    const FAMILY: Family = Family::Unix;
    const PATH_SEPARATOR: char = '/';
    const LINE_ENDING: &'static str = "\n";
    // The default APFS/HFS+ volume is case-insensitive but case-preserving.
    const CASE_SENSITIVE_FS: bool = false;
}
