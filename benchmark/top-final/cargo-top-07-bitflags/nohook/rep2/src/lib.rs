use bitflags::bitflags;

bitflags! {
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
    fn removes_flag() {
        let mut perms = Permissions::READ | Permissions::WRITE | Permissions::EXECUTE;
        perms.remove(Permissions::WRITE);
        assert!(!perms.contains(Permissions::WRITE));
        assert!(perms.contains(Permissions::READ));
    }

    #[test]
    fn empty_and_all() {
        assert!(Permissions::empty().is_empty());
        assert!(Permissions::all().contains(Permissions::DELETE));
    }
}
