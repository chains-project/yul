//! Fallback for targets that are not yet modelled.
//!
//! This module keeps the crate compiling on every target without forcing every
//! consumer to gate their code. Values are deliberately conservative.

use crate::{Family, Platform};

pub(crate) const PLATFORM: Platform = Platform::Unknown;
pub(crate) const FAMILY: Family = Family::Unknown;
pub(crate) const PATH_SEPARATOR: char = '/';
pub(crate) const PATH_LIST_SEPARATOR: char = ':';
pub(crate) const LINE_ENDING: &str = "\n";
pub(crate) const EXECUTABLE_SUFFIX: &str = "";
