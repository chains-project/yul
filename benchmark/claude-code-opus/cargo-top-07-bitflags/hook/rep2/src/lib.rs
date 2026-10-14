//! Type-safe bitflag constants that can be combined and checked.
//!
//! ```
//! use flagset::Permissions;
//!
//! let rw = Permissions::READ | Permissions::WRITE;
//! assert!(rw.contains(Permissions::READ));
//! assert!(!rw.contains(Permissions::EXECUTE));
//! assert!(rw.intersects(Permissions::WRITE | Permissions::EXECUTE));
//! ```

use bitflags::bitflags;

bitflags! {
    /// A set of access permissions.
    ///
    /// Each constant occupies a distinct bit, so values can be combined with
    /// `|`, intersected with `&`, removed with `-`, and toggled with `^`.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Default)]
    pub struct Permissions: u32 {
        const READ    = 1 << 0;
        const WRITE   = 1 << 1;
        const EXECUTE = 1 << 2;

        /// Convenience combination of all permissions.
        const ALL = Self::READ.bits() | Self::WRITE.bits() | Self::EXECUTE.bits();
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
        assert_eq!(flags.bits(), 0b101);
    }

    #[test]
    fn insert_and_remove() {
        let mut flags = Permissions::empty();
        flags.insert(Permissions::WRITE);
        assert_eq!(flags, Permissions::WRITE);
        flags.remove(Permissions::WRITE);
        assert!(flags.is_empty());
    }

    #[test]
    fn all_contains_every_flag() {
        assert_eq!(Permissions::ALL, Permissions::all());
        assert!(Permissions::ALL.contains(Permissions::READ | Permissions::WRITE));
    }

    #[test]
    fn rejects_unknown_bits() {
        assert_eq!(Permissions::from_bits(0b1000), None);
        assert_eq!(
            Permissions::from_bits_truncate(0b1011),
            Permissions::READ | Permissions::WRITE
        );
    }
}
