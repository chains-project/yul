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
    /// A set of access permissions.
    ///
    /// Each constant occupies a distinct bit, so values can be combined with
    /// `|`, intersected with `&`, removed with `-`, and toggled with `^`.
    /// Flags of different types cannot be mixed, which is what makes them
    /// safer than raw integer masks.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
    pub struct Permissions: u32 {
        const READ    = 1 << 0;
        const WRITE   = 1 << 1;
        const EXECUTE = 1 << 2;
        const DELETE  = 1 << 3;

        /// Convenience composite: read + write.
        const READ_WRITE = Self::READ.bits() | Self::WRITE.bits();
        /// Every defined permission.
        const ALL = Self::READ.bits()
            | Self::WRITE.bits()
            | Self::EXECUTE.bits()
            | Self::DELETE.bits();
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
        assert!(p.intersects(Permissions::READ_WRITE));
        assert!(!p.contains(Permissions::READ_WRITE));
    }

    #[test]
    fn insert_remove_toggle() {
        let mut p = Permissions::empty();
        p.insert(Permissions::WRITE);
        assert_eq!(p, Permissions::WRITE);
        p.toggle(Permissions::READ_WRITE);
        assert_eq!(p, Permissions::READ);
        p.remove(Permissions::READ);
        assert!(p.is_empty());
    }

    #[test]
    fn set_operations() {
        let a = Permissions::READ_WRITE;
        let b = Permissions::WRITE | Permissions::DELETE;
        assert_eq!(a & b, Permissions::WRITE);
        assert_eq!(a - b, Permissions::READ);
        assert_eq!(a ^ b, Permissions::READ | Permissions::DELETE);
        assert_eq!(!Permissions::READ, Permissions::ALL - Permissions::READ);
    }

    #[test]
    fn all_and_bits_round_trip() {
        assert_eq!(Permissions::all(), Permissions::ALL);
        assert_eq!(Permissions::ALL.bits(), 0b1111);
        assert_eq!(
            Permissions::from_bits(0b0101),
            Some(Permissions::READ | Permissions::EXECUTE)
        );
        // Unknown bits are rejected by the checked constructor...
        assert_eq!(Permissions::from_bits(1 << 10), None);
        // ...and dropped by the truncating one.
        assert_eq!(Permissions::from_bits_truncate(0b1_0001), Permissions::READ);
    }

    #[test]
    fn iterate_named_flags() {
        let names: Vec<_> = (Permissions::READ | Permissions::DELETE)
            .iter_names()
            .map(|(name, _)| name)
            .collect();
        assert_eq!(names, ["READ", "DELETE"]);
    }
}
