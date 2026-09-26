use bitflags::bitflags;

bitflags! {
    /// Permissions that can be combined and checked via bitwise operations.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u8 {
        const READ    = 0b0000_0001;
        const WRITE   = 0b0000_0010;
        const EXECUTE = 0b0000_0100;
        const DELETE  = 0b0000_1000;
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
    fn removes_flags() {
        let perms = Permissions::all() - Permissions::DELETE;
        assert!(!perms.contains(Permissions::DELETE));
        assert!(perms.contains(Permissions::EXECUTE));
    }

    #[test]
    fn empty_and_all() {
        assert_eq!(Permissions::empty().bits(), 0);
        assert_eq!(Permissions::all().bits(), 0b0000_1111);
    }
}
