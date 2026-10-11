use bitflags::bitflags;

bitflags! {
    /// A type-safe set of permissions that can be combined and queried.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u8 {
        const READ    = 0b0000_0001;
        const WRITE   = 0b0000_0010;
        const EXECUTE = 0b0000_0100;
        /// Convenience alias: everything except `EXECUTE`.
        const MODIFY  = Self::READ.bits() | Self::WRITE.bits();
    }
}

impl Permissions {
    /// Returns `true` if every flag in `other` is present in `self`.
    pub fn contains_all(&self, other: Permissions) -> bool {
        self.contains(other)
    }

    /// Returns `true` if any flag in `other` is present in `self`.
    pub fn intersects_any(&self, other: Permissions) -> bool {
        self.intersects(other)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combines_flags() {
        let flags = Permissions::READ | Permissions::WRITE;
        assert_eq!(flags, Permissions::READ | Permissions::WRITE);
        assert!(flags.contains(Permissions::READ));
        assert!(flags.contains(Permissions::WRITE));
        assert!(!flags.contains(Permissions::EXECUTE));
    }

    #[test]
    fn checks_membership() {
        let flags = Permissions::READ | Permissions::EXECUTE;
        assert!(flags.contains_all(Permissions::READ));
        assert!(!flags.contains_all(Permissions::READ | Permissions::WRITE));
        assert!(flags.intersects_any(Permissions::EXECUTE | Permissions::WRITE));
    }

    #[test]
    fn supports_complements() {
        let read_only = Permissions::READ;
        let rest = !read_only;
        assert!(rest.contains(Permissions::WRITE));
        assert!(!rest.contains(Permissions::READ));
    }

    #[test]
    fn alias_flag_works() {
        assert!(Permissions::MODIFY.contains(Permissions::READ));
        assert!(Permissions::MODIFY.contains(Permissions::WRITE));
        assert!(!Permissions::MODIFY.contains(Permissions::EXECUTE));
    }
}
