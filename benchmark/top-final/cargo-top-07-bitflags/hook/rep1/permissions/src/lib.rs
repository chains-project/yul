use bitflags::bitflags;

bitflags! {
    /// A type-safe set of file permission flags.
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
    fn combines_flags_with_bitor() {
        let perms = Permissions::READ | Permissions::WRITE;
        assert!(perms.contains(Permissions::READ));
        assert!(perms.contains(Permissions::WRITE));
        assert!(!perms.contains(Permissions::EXECUTE));
    }

    #[test]
    fn checks_intersection() {
        let perms = Permissions::READ | Permissions::EXECUTE;
        assert!(perms.intersects(Permissions::EXECUTE | Permissions::DELETE));
        assert!(!perms.intersects(Permissions::WRITE | Permissions::DELETE));
    }

    #[test]
    fn removes_a_flag() {
        let mut perms = Permissions::READ | Permissions::WRITE | Permissions::EXECUTE;
        perms.remove(Permissions::WRITE);
        assert_eq!(perms, Permissions::READ | Permissions::EXECUTE);
    }

    #[test]
    fn empty_and_all_constants() {
        assert!(Permissions::empty().is_empty());
        assert!(Permissions::all().contains(Permissions::DELETE));
    }
}
