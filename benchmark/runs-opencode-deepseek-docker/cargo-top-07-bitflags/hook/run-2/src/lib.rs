//! Type-safe bitflag constants that can be combined and checked.
//!
//! Flags are declared with the [`bitflags`] macro, which generates a newtype
//! over an integer. This keeps flags type-safe: a `Permissions` value can only
//! be combined with another `Permissions`, never with a raw integer or an
//! unrelated flag type.
//!
//! ```
//! use flags::Permissions;
//!
//! let mut perms = Permissions::READ | Permissions::WRITE;
//! assert!(perms.contains(Permissions::READ));
//! assert!(!perms.contains(Permissions::DELETE));
//!
//! perms.remove(Permissions::WRITE);
//! assert!(!perms.contains(Permissions::READ_WRITE));
//! ```

use bitflags::bitflags;

bitflags! {
    /// A set of permissions for a resource.
    ///
    /// Individual flags can be combined with `|`, intersected with `&`,
    /// toggled with `^`, and inverted with `!`.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u32 {
        /// Permission to read a resource.
        const READ = 0b0000_0001;
        /// Permission to write to a resource.
        const WRITE = 0b0000_0010;
        /// Permission to execute a resource.
        const EXECUTE = 0b0000_0100;
        /// Permission to delete a resource.
        const DELETE = 0b0000_1000;

        /// Read and write access, combined.
        const READ_WRITE = Self::READ.bits() | Self::WRITE.bits();
        /// Every permission.
        const ALL = Self::READ.bits()
            | Self::WRITE.bits()
            | Self::EXECUTE.bits()
            | Self::DELETE.bits();
    }
}

impl Permissions {
    /// Returns `true` if every flag set in `other` is also set in `self`.
    pub fn has(self, other: Self) -> bool {
        self.contains(other)
    }

    /// Returns a copy of `self` with every flag in `other` set.
    pub fn with(self, other: Self) -> Self {
        self | other
    }

    /// Returns a copy of `self` with every flag in `other` cleared.
    pub fn without(self, other: Self) -> Self {
        self & !other
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combine_with_bitwise_or() {
        let perms = Permissions::READ | Permissions::WRITE;
        assert_eq!(perms, Permissions::READ_WRITE);
    }

    #[test]
    fn contains_checks_every_requested_flag() {
        let perms = Permissions::READ | Permissions::WRITE;
        assert!(perms.contains(Permissions::READ));
        assert!(perms.contains(Permissions::READ_WRITE));
        assert!(!perms.contains(Permissions::DELETE));
    }

    #[test]
    fn intersects_detects_any_overlap() {
        let perms = Permissions::READ | Permissions::EXECUTE;
        assert!(perms.intersects(Permissions::READ_WRITE));
        assert!(!perms.intersects(Permissions::WRITE | Permissions::DELETE));
    }

    #[test]
    fn set_and_clear_flags_in_place() {
        let mut perms = Permissions::empty();
        perms.insert(Permissions::WRITE);
        assert_eq!(perms, Permissions::WRITE);

        perms.remove(Permissions::WRITE);
        assert!(perms.is_empty());
    }

    #[test]
    fn helpers_build_new_sets() {
        let perms = Permissions::READ.with(Permissions::WRITE);
        assert_eq!(perms, Permissions::READ_WRITE);

        let perms = perms.without(Permissions::READ);
        assert_eq!(perms, Permissions::WRITE);
        assert!(Permissions::READ_WRITE.has(Permissions::READ));
    }

    #[test]
    fn all_and_empty() {
        assert_eq!(
            Permissions::READ | Permissions::WRITE | Permissions::EXECUTE | Permissions::DELETE,
            Permissions::ALL
        );
        assert!(Permissions::empty().is_empty());
    }
}
