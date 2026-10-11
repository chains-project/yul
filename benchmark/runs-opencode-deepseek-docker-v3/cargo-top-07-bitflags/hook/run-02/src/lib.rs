//! A tiny library demonstrating type-safe bitflag constants.
//!
//! Flags are declared with the [`bitflags`] macro, which produces a strongly
//! typed set. Individual flags can be combined with `|`, intersected with `&`,
//! and queried with [`Flags::contains`].

use bitflags::bitflags;

bitflags! {
    /// A set of permission bits.
    ///
    /// ```
    /// use bitflags_lib::Permissions;
    ///
    /// let mut perms = Permissions::READ | Permissions::WRITE;
    /// assert!(perms.contains(Permissions::READ));
    /// assert!(!perms.contains(Permissions::EXECUTE));
    ///
    /// perms.insert(Permissions::EXECUTE);
    /// assert_eq!(perms, Permissions::all());
    ///
    /// perms.remove(Permissions::WRITE);
    /// assert_eq!(perms, Permissions::READ | Permissions::EXECUTE);
    /// ```
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u8 {
        /// Allows reading.
        const READ    = 0b0000_0001;
        /// Allows writing.
        const WRITE   = 0b0000_0010;
        /// Allows executing.
        const EXECUTE = 0b0000_0100;
    }
}

impl Permissions {
    /// Returns `true` if every flag in `self` is also present in `other`.
    ///
    /// This is a convenience wrapper around [`Permissions::contains`] that
    /// reads naturally when checking whether one set is a superset of another.
    pub fn is_superset_of(self, other: Self) -> bool {
        self.contains(other)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combine_with_or() {
        let rw = Permissions::READ | Permissions::WRITE;
        assert!(rw.contains(Permissions::READ));
        assert!(rw.contains(Permissions::WRITE));
        assert!(!rw.contains(Permissions::EXECUTE));
    }

    #[test]
    fn intersect_with_and() {
        let rw = Permissions::READ | Permissions::WRITE;
        let we = Permissions::WRITE | Permissions::EXECUTE;
        assert_eq!(rw & we, Permissions::WRITE);
    }

    #[test]
    fn mutate_in_place() {
        let mut perms = Permissions::empty();
        perms.insert(Permissions::READ);
        perms.insert(Permissions::EXECUTE);
        assert_eq!(perms, Permissions::READ | Permissions::EXECUTE);

        perms.remove(Permissions::READ);
        assert_eq!(perms, Permissions::EXECUTE);

        perms.toggle(Permissions::EXECUTE);
        assert!(perms.is_empty());
    }

    #[test]
    fn superset_check() {
        let all = Permissions::all();
        assert!(all.is_superset_of(Permissions::READ | Permissions::WRITE));
        assert!(!Permissions::READ.is_superset_of(all));
    }
}
