use super::Platform;
use crate::Family;

/// Linux backend.
pub(crate) struct Imp;

impl Platform for Imp {
    const NAME: &'static str = "linux";
    const FAMILY: Family = Family::Unix;
    const PATH_SEPARATOR: char = '/';
    const LINE_ENDING: &'static str = "\n";
    const CASE_SENSITIVE_FS: bool = true;
}
