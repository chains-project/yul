use crate::{Family, Platform};

pub(crate) use super::unix_common::{
    EXECUTABLE_SUFFIX, LINE_ENDING, PATH_LIST_SEPARATOR, PATH_SEPARATOR,
};

pub(crate) const PLATFORM: Platform = Platform::FreeBsd;
pub(crate) const FAMILY: Family = Family::Unix;
