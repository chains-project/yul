use bitflags::bitflags;

bitflags! {
    /// A type-safe set of permissions that can be combined and queried.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u8 {
        /// Permission to read a resource.
        const READ    = 0b0000_0001;
        /// Permission to write a resource.
        const WRITE   = 0b0000_0010;
        /// Permission to execute a resource.
        const EXECUTE = 0b0000_0100;
        /// Permission to delete a resource.
        const DELETE  = 0b0000_1000;
    }
}

impl Permissions {
    /// Returns the permissions implied by `READ` and `WRITE` together.
    pub fn read_write() -> Self {
        Self::READ | Self::WRITE
    }

    /// Returns `true` if every permission in `other` is also in `self`.
    pub fn grants(&self, other: Self) -> bool {
        self.contains(other)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combine_with_bitwise_or() {
        let combined = Permissions::READ | Permissions::WRITE;
        assert!(combined.contains(Permissions::READ));
        assert!(combined.contains(Permissions::WRITE));
        assert!(!combined.contains(Permissions::EXECUTE));
    }

    #[test]
    fn intersect_with_bitwise_and() {
        let perms = Permissions::READ | Permissions::WRITE;
        let overlap = perms & Permissions::WRITE;
        assert_eq!(overlap, Permissions::WRITE);
        assert!(overlap.contains(Permissions::WRITE));
    }

    #[test]
    fn toggle_and_remove() {
        let mut perms = Permissions::READ | Permissions::WRITE;
        perms.remove(Permissions::READ);
        assert!(!perms.contains(Permissions::READ));
        perms.toggle(Permissions::EXECUTE);
        assert!(perms.contains(Permissions::EXECUTE));
    }

    #[test]
    fn helper_and_grants() {
        let rw = Permissions::read_write();
        assert_eq!(rw, Permissions::READ | Permissions::WRITE);
        assert!(rw.grants(Permissions::READ));
        assert!(!rw.grants(Permissions::DELETE));
    }

    #[test]
    fn empty_set_is_falsy() {
        assert!(Permissions::empty().is_empty());
        assert!(Permissions::all().contains(Permissions::read_write()));
    }
}
