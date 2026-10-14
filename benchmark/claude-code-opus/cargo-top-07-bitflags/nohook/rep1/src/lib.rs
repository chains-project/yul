//! Type-safe bitflag constants that can be combined and checked.
//!
//! ```
//! use flagset_lib::Permissions;
//!
//! let rw = Permissions::READ | Permissions::WRITE;
//! assert!(rw.contains(Permissions::READ));
//! assert!(!rw.contains(Permissions::EXECUTE));
//! assert_eq!(rw | Permissions::EXECUTE, Permissions::ALL);
//! ```

use bitflags::bitflags;

bitflags! {
    /// A set of permission flags.
    ///
    /// Each flag occupies a distinct bit, so flags can be combined with `|`,
    /// intersected with `&`, removed with `-`, and toggled with `^`.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
    pub struct Permissions: u32 {
        const READ    = 1 << 0;
        const WRITE   = 1 << 1;
        const EXECUTE = 1 << 2;

        /// Composite flag: every defined permission.
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
        assert!(flags.intersects(Permissions::WRITE | Permissions::EXECUTE));
    }

    #[test]
    fn insert_remove_toggle() {
        let mut flags = Permissions::empty();
        flags.insert(Permissions::WRITE);
        assert_eq!(flags, Permissions::WRITE);

        flags.toggle(Permissions::READ);
        assert_eq!(flags, Permissions::READ | Permissions::WRITE);

        flags.remove(Permissions::WRITE);
        assert_eq!(flags, Permissions::READ);
    }

    #[test]
    fn all_composite() {
        assert_eq!(Permissions::ALL, Permissions::all());
        assert_eq!(
            Permissions::ALL - Permissions::WRITE,
            Permissions::READ | Permissions::EXECUTE
        );
    }

    #[test]
    fn from_bits_rejects_unknown() {
        assert_eq!(
            Permissions::from_bits(0b011),
            Some(Permissions::READ | Permissions::WRITE)
        );
        assert_eq!(Permissions::from_bits(0b1000), None);
        assert_eq!(Permissions::from_bits_truncate(0b1111), Permissions::ALL);
    }
}
