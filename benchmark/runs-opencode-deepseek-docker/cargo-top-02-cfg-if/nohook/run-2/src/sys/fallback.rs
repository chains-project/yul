use super::Platform;
use crate::Family;

/// Backend for targets with no dedicated implementation.
///
/// It reports the target's own `std` name and assumes conservative Unix-like
/// defaults, which keeps exotic targets compiling instead of failing.
pub(crate) struct Imp;

impl Platform for Imp {
    const NAME: &'static str = std::env::consts::OS;
    const FAMILY: Family = Family::Other;
    const PATH_SEPARATOR: char = '/';
    const LINE_ENDING: &'static str = "\n";
    const CASE_SENSITIVE_FS: bool = true;
}
