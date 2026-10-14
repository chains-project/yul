//! Type-safe bitflag constants that can be combined and checked.
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
    /// A set of file-style permission flags.
    ///
    /// Each constant occupies a distinct bit, so flags can be combined with
    /// `|`, intersected with `&`, removed with `-`, and toggled with `^`.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
    pub struct Permissions: u32 {
        const READ    = 1 << 0;
        const WRITE   = 1 << 1;
        const EXECUTE = 1 << 2;

        /// Convenience composite of all individual flags.
        const ALL = Self::READ.bits() | Self::WRITE.bits() | Self::EXECUTE.bits();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combine_and_check() {
        let flags = Permissions::READ | Permissions::WRITE;
        assert!(flags.contains(Permissions::READ));
        assert!(flags.contains(Permissions::WRITE));
        assert!(!flags.contains(Permissions::EXECUTE));
        assert!(flags.intersects(Permissions::WRITE | Permissions::EXECUTE));
    }

    #[test]
    fn insert_remove_toggle() {
        let mut flags = Permissions::empty();
        flags.insert(Permissions::EXECUTE);
        assert_eq!(flags, Permissions::EXECUTE);

        flags.toggle(Permissions::READ);
        assert_eq!(flags, Permissions::READ | Permissions::EXECUTE);

        flags.remove(Permissions::EXECUTE);
        assert_eq!(flags, Permissions::READ);
    }

    #[test]
    fn all_and_empty() {
        assert_eq!(Permissions::all(), Permissions::ALL);
        assert!(Permissions::empty().is_empty());
        assert_eq!(
            Permissions::ALL - Permissions::WRITE,
            Permissions::READ | Permissions::EXECUTE
        );
    }

    #[test]
    fn bits_round_trip() {
        let flags = Permissions::READ | Permissions::EXECUTE;
        assert_eq!(flags.bits(), 0b101);
        assert_eq!(Permissions::from_bits(0b101), Some(flags));
        // Unknown bits are rejected by the checked constructor.
        assert_eq!(Permissions::from_bits(0b1000), None);
        assert_eq!(Permissions::from_bits_truncate(0b1101), flags);
    }
}
