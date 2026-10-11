use bitflags::bitflags;

bitflags! {
    /// A type-safe set of permissions.
    ///
    /// Flags can be combined with `|`, intersected with `&`, and tested for
    /// membership with [`Permissions::contains`].
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u32 {
        const READ    = 0b0000_0001;
        const WRITE   = 0b0000_0010;
        const EXECUTE = 0b0000_0100;
        const DELETE  = 0b0000_1000;

        const ALL = Self::READ.bits()
            | Self::WRITE.bits()
            | Self::EXECUTE.bits()
            | Self::DELETE.bits();
    }
}

impl Permissions {
    /// Returns `true` if every flag in `other` is present in `self`.
    pub fn has(self, other: Self) -> bool {
        self.contains(other)
    }

    /// Returns a set with `other` added.
    pub fn with(self, other: Self) -> Self {
        self | other
    }

    /// Returns a set with `other` removed.
    pub fn without(self, other: Self) -> Self {
        self & !other
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combine_and_check() {
        let rw = Permissions::READ | Permissions::WRITE;

        assert!(rw.contains(Permissions::READ));
        assert!(rw.contains(Permissions::WRITE));
        assert!(!rw.contains(Permissions::EXECUTE));
        assert!(rw.has(Permissions::READ | Permissions::WRITE));
    }

    #[test]
    fn add_and_remove() {
        let perms = Permissions::READ.with(Permissions::EXECUTE);
        assert!(perms.contains(Permissions::EXECUTE));

        let perms = perms.without(Permissions::READ);
        assert!(!perms.contains(Permissions::READ));
        assert!(perms.contains(Permissions::EXECUTE));
    }

    #[test]
    fn all_contains_every_flag() {
        assert!(Permissions::ALL.contains(Permissions::READ));
        assert!(Permissions::ALL.contains(Permissions::WRITE));
        assert!(Permissions::ALL.contains(Permissions::EXECUTE));
        assert!(Permissions::ALL.contains(Permissions::DELETE));
    }

    #[test]
    fn empty_is_the_identity() {
        assert!(Permissions::empty().is_empty());
        assert_eq!(Permissions::empty() | Permissions::READ, Permissions::READ);
    }
}
