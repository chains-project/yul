//! Type-safe bitflag constants that can be combined and checked.
//!
//! ```
//! use flagset_lib::Permissions;
//!
//! let rw = Permissions::READ | Permissions::WRITE;
//! assert!(rw.contains(Permissions::READ));
//! assert!(!rw.contains(Permissions::EXECUTE));
//! assert_eq!(rw.bits(), 0b011);
//! ```

use bitflags::bitflags;

bitflags! {
    /// A set of access permissions.
    ///
    /// Each constant occupies a distinct bit, so values can be combined with
    /// `|`, intersected with `&`, removed with `-`, and toggled with `^`.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Default)]
    pub struct Permissions: u32 {
        const READ    = 1 << 0;
        const WRITE   = 1 << 1;
        const EXECUTE = 1 << 2;

        /// Every defined permission.
        const ALL = Self::READ.bits() | Self::WRITE.bits() | Self::EXECUTE.bits();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combine_and_check() {
        let p = Permissions::READ | Permissions::EXECUTE;
        assert!(p.contains(Permissions::READ));
        assert!(p.contains(Permissions::EXECUTE));
        assert!(!p.contains(Permissions::WRITE));
        assert!(p.intersects(Permissions::READ | Permissions::WRITE));
    }

    #[test]
    fn insert_remove_toggle() {
        let mut p = Permissions::empty();
        p.insert(Permissions::WRITE);
        assert_eq!(p, Permissions::WRITE);
        p.toggle(Permissions::READ);
        assert_eq!(p, Permissions::READ | Permissions::WRITE);
        p.remove(Permissions::WRITE);
        assert_eq!(p, Permissions::READ);
    }

    #[test]
    fn all_and_empty() {
        assert_eq!(Permissions::all(), Permissions::ALL);
        assert!(Permissions::default().is_empty());
        assert_eq!(
            Permissions::ALL - Permissions::WRITE,
            Permissions::READ | Permissions::EXECUTE
        );
    }

    #[test]
    fn from_bits_rejects_unknown() {
        assert_eq!(
            Permissions::from_bits(0b101),
            Some(Permissions::READ | Permissions::EXECUTE)
        );
        assert_eq!(Permissions::from_bits(0b1000), None);
        assert_eq!(Permissions::from_bits_truncate(0b1001), Permissions::READ);
    }
}
