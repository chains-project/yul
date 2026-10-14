//! Type-safe bitflag constants that can be combined and checked.
//!
//! Flags are defined with the [`bitflags`] crate, which generates a newtype
//! over an integer so that flags from different sets can't be mixed up.
//!
//! ```
//! use flagset_lib::Permissions;
//!
//! let rw = Permissions::READ | Permissions::WRITE;
//! assert!(rw.contains(Permissions::READ));
//! assert!(!rw.contains(Permissions::EXECUTE));
//! ```

use bitflags::bitflags;

bitflags! {
    /// File-style access permissions.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
    pub struct Permissions: u32 {
        const READ    = 1 << 0;
        const WRITE   = 1 << 1;
        const EXECUTE = 1 << 2;

        /// Composite flag: read and write.
        const READ_WRITE = Self::READ.bits() | Self::WRITE.bits();
        /// Composite flag: every permission.
        const ALL = Self::READ.bits() | Self::WRITE.bits() | Self::EXECUTE.bits();
    }
}

impl Default for Permissions {
    fn default() -> Self {
        Self::empty()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combine_and_check() {
        let flags = Permissions::READ | Permissions::EXECUTE;
        assert!(flags.contains(Permissions::READ));
        assert!(flags.contains(Permissions::EXECUTE));
        assert!(!flags.contains(Permissions::WRITE));
        assert!(flags.intersects(Permissions::READ_WRITE));
        assert!(!flags.contains(Permissions::READ_WRITE));
    }

    #[test]
    fn insert_remove_toggle() {
        let mut flags = Permissions::default();
        assert!(flags.is_empty());

        flags.insert(Permissions::WRITE);
        flags.toggle(Permissions::READ);
        assert_eq!(flags, Permissions::READ_WRITE);

        flags.remove(Permissions::WRITE);
        assert_eq!(flags, Permissions::READ);
    }

    #[test]
    fn set_operations() {
        let a = Permissions::READ_WRITE;
        let b = Permissions::WRITE | Permissions::EXECUTE;
        assert_eq!(a & b, Permissions::WRITE);
        assert_eq!(a | b, Permissions::ALL);
        assert_eq!(a - b, Permissions::READ);
        assert_eq!(!a, Permissions::EXECUTE);
        assert!(Permissions::ALL.is_all());
    }

    #[test]
    fn bits_roundtrip() {
        assert_eq!(
            Permissions::from_bits(0b101),
            Some(Permissions::READ | Permissions::EXECUTE)
        );
        // Unknown bits are rejected by `from_bits` and dropped by `from_bits_truncate`.
        assert_eq!(Permissions::from_bits(0b1000), None);
        assert_eq!(Permissions::from_bits_truncate(0b1001), Permissions::READ);
    }
}
