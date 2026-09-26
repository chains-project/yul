use bitflags::bitflags;

bitflags! {
    /// Permission flags that can be combined and checked in a type-safe way.
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
    fn checks_intersection_and_removal() {
        let mut perms = Permissions::all();
        assert!(perms.intersects(Permissions::DELETE));

        perms.remove(Permissions::DELETE);
        assert!(!perms.contains(Permissions::DELETE));
        assert!(perms.contains(Permissions::EXECUTE));
    }

    #[test]
    fn empty_has_no_flags_set() {
        let perms = Permissions::empty();
        assert_eq!(perms.bits(), 0);
    }
}
