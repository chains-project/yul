use bitflags::bitflags;

bitflags! {
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u32 {
        const READ    = 0b0000_0001;
        const WRITE   = 0b0000_0010;
        const EXECUTE = 0b0000_0100;
        const ALL     = Self::READ.bits() | Self::WRITE.bits() | Self::EXECUTE.bits();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combines_flags_with_bitor() {
        let rw = Permissions::READ | Permissions::WRITE;
        assert!(rw.contains(Permissions::READ));
        assert!(rw.contains(Permissions::WRITE));
        assert!(!rw.contains(Permissions::EXECUTE));
    }

    #[test]
    fn checks_intersection() {
        let rw = Permissions::READ | Permissions::WRITE;
        assert!(rw.intersects(Permissions::WRITE | Permissions::EXECUTE));
        assert!(!rw.intersects(Permissions::EXECUTE));
    }

    #[test]
    fn inserts_and_removes_flags() {
        let mut perms = Permissions::READ;
        perms.insert(Permissions::WRITE);
        assert_eq!(perms, Permissions::READ | Permissions::WRITE);
        perms.remove(Permissions::READ);
        assert_eq!(perms, Permissions::WRITE);
    }

    #[test]
    fn all_contains_every_flag() {
        assert!(Permissions::ALL.contains(Permissions::READ));
        assert!(Permissions::ALL.contains(Permissions::WRITE));
        assert!(Permissions::ALL.contains(Permissions::EXECUTE));
    }

    #[test]
    fn empty_set_is_empty() {
        assert!(Permissions::empty().is_empty());
        assert_eq!(Permissions::empty().bits(), 0);
        assert!(!Permissions::READ.is_empty());
    }
}
