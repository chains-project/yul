use super::Platform;
use crate::Family;

/// Windows backend.
pub(crate) struct Imp;

impl Platform for Imp {
    const NAME: &'static str = "windows";
    const FAMILY: Family = Family::Windows;
    const PATH_SEPARATOR: char = '\\';
    const LINE_ENDING: &'static str = "\r\n";
    const CASE_SENSITIVE_FS: bool = false;
}
