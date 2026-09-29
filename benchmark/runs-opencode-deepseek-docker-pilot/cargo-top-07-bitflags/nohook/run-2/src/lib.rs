//! Type-safe bitflag sets for `flagset`.
//!
//! [`Permissions`] is a compile-time-checked set of flags. Individual flags can
//! be combined with the bitwise operators (`|`, `&`, `^`) and queried with the
//! [`contains`](Permissions::contains) and
//! [`intersects`](Permissions::intersects) methods.

use bitflags::bitflags;

bitflags! {
    /// A set of filesystem permissions stored as a bitset.
    ///
    /// Each constant is a distinct set whose members can be freely combined. A
    /// value of this type can hold any combination of the constants below.
    ///
    /// # Examples
    ///
    /// ```
    /// use flagset::Permissions;
    ///
    /// let mut perms = Permissions::READ | Permissions::WRITE;
    /// assert!(perms.contains(Permissions::READ));
    /// assert!(!perms.intersects(Permissions::EXECUTE));
    ///
    /// perms.insert(Permissions::EXECUTE);
    /// assert!(perms.contains(Permissions::ALL));
    /// ```
    #[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
    pub struct Permissions: u8 {
        /// Allow reading the associated resource.
        const READ = 0b0000_0001;
        /// Allow modifying the associated resource.
        const WRITE = 0b0000_0010;
        /// Allow running the associated resource.
        const EXECUTE = 0b0000_0100;
        /// The set of all supported flags.
        const ALL = Self::READ.bits() | Self::WRITE.bits() | Self::EXECUTE.bits();
    }
}

impl Permissions {
    /// Returns `true` if `self` contains every flag in `other`.
    ///
    /// This is a readable alias for [`Permissions::contains`] and accepts the
    /// flags by value as well as by reference.
    ///
    /// # Examples
    ///
    /// ```
    /// use flagset::Permissions;
    ///
    /// let perms = Permissions::READ | Permissions::WRITE;
    /// assert!(perms.has(Permissions::READ));
    /// assert!(!perms.has(Permissions::EXECUTE));
    /// ```
    pub fn has(self, other: Self) -> bool {
        self.contains(other)
    }

    /// Returns a new set with the flags in `other` added.
    ///
    /// # Examples
    ///
    /// ```
    /// use flagset::Permissions;
    ///
    /// let perms = Permissions::READ.with(Permissions::WRITE);
    /// assert_eq!(perms, Permissions::READ | Permissions::WRITE);
    /// ```
    pub fn with(self, other: Self) -> Self {
        self | other
    }

    /// Returns a new set with the flags in `other` removed.
    ///
    /// # Examples
    ///
    /// ```
    /// use flagset::Permissions;
    ///
    /// let perms = Permissions::ALL.without(Permissions::EXECUTE);
    /// assert!(!perms.contains(Permissions::EXECUTE));
    /// ```
    pub fn without(self, other: Self) -> Self {
        self & !other
    }

    /// Returns `true` if the set is exactly equal to one of the defined flags.
    ///
    /// # Examples
    ///
    /// ```
    /// use flagset::Permissions;
    ///
    /// assert!(Permissions::READ.is_single());
    /// assert!(!(Permissions::READ | Permissions::WRITE).is_single());
    /// ```
    pub fn is_single(self) -> bool {
        self.bits().is_power_of_two()
    }
}

#[cfg(test)]
mod tests {
    use super::Permissions;

    #[test]
    fn flags_are_distinct() {
        assert_ne!(Permissions::READ, Permissions::WRITE);
        assert_ne!(Permissions::WRITE, Permissions::EXECUTE);
        assert_eq!(
            Permissions::ALL,
            Permissions::READ | Permissions::WRITE | Permissions::EXECUTE
        );
    }

    #[test]
    fn combine_with_operators() {
        let perms = Permissions::READ | Permissions::EXECUTE;
        assert!(perms.contains(Permissions::READ));
        assert!(perms.contains(Permissions::EXECUTE));
        assert!(!perms.contains(Permissions::WRITE));

        let without_exec = perms & !Permissions::EXECUTE;
        assert_eq!(without_exec, Permissions::READ);
    }

    #[test]
    fn contains_and_intersects() {
        let perms = Permissions::READ | Permissions::WRITE;
        assert!(perms.has(Permissions::READ));
        assert!(perms.contains(Permissions::READ | Permissions::WRITE));
        assert!(!perms.contains(Permissions::ALL));
        assert!(perms.intersects(Permissions::WRITE | Permissions::EXECUTE));
    }

    #[test]
    fn insert_and_remove() {
        let mut perms = Permissions::empty();
        assert!(perms.is_empty());

        perms.insert(Permissions::READ);
        assert!(perms.is_single());

        perms.insert(Permissions::WRITE);
        assert_eq!(perms, Permissions::READ | Permissions::WRITE);

        perms.remove(Permissions::READ);
        assert_eq!(perms, Permissions::WRITE);

        perms.toggle(Permissions::WRITE);
        assert!(perms.is_empty());
    }

    #[test]
    fn immutable_helpers() {
        assert_eq!(
            Permissions::READ.with(Permissions::WRITE),
            Permissions::READ | Permissions::WRITE
        );
        assert_eq!(
            Permissions::ALL.without(Permissions::EXECUTE),
            Permissions::READ | Permissions::WRITE
        );
    }

    #[test]
    fn roundtrips_through_bits() {
        let perms = Permissions::READ | Permissions::EXECUTE;
        let bits = perms.bits();
        assert_eq!(Permissions::from_bits(bits), Some(perms));
        assert_eq!(Permissions::from_bits(0b1000_0000), None);
    }
}
