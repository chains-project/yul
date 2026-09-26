use bitflags::bitflags;

bitflags! {
    /// Permissions that can be granted to a resource, combined as a bitmask.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u32 {
        const READ    = 1 << 0;
        const WRITE   = 1 << 1;
        const EXECUTE = 1 << 2;
        const DELETE  = 1 << 3;
    }
}

impl Permissions {
    pub fn is_readonly(&self) -> bool {
        *self == Permissions::READ
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combines_flags() {
        let perms = Permissions::READ | Permissions::WRITE;
        assert!(perms.contains(Permissions::READ));
        assert!(perms.contains(Permissions::WRITE));
        assert!(!perms.contains(Permissions::EXECUTE));
    }

    #[test]
    fn checks_readonly() {
        assert!(Permissions::READ.is_readonly());
        assert!(!(Permissions::READ | Permissions::WRITE).is_readonly());
    }

    #[test]
    fn removes_flags() {
        let mut perms = Permissions::READ | Permissions::WRITE | Permissions::EXECUTE;
        perms.remove(Permissions::WRITE);
        assert_eq!(perms, Permissions::READ | Permissions::EXECUTE);
    }

    #[test]
    fn empty_and_all() {
        assert!(Permissions::empty().is_empty());
        assert!(Permissions::all().contains(Permissions::DELETE));
    }
}
