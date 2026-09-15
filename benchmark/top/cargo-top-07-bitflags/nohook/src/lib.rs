use bitflags::bitflags;

bitflags! {
    /// Permissions that can be granted to a user, combined via bitwise OR.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u32 {
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
    fn checks_intersection_and_union() {
        let rw = Permissions::READ | Permissions::WRITE;
        let we = Permissions::WRITE | Permissions::EXECUTE;

        assert_eq!(rw.intersection(we), Permissions::WRITE);
        assert_eq!(
            rw.union(we),
            Permissions::READ | Permissions::WRITE | Permissions::EXECUTE
        );
    }

    #[test]
    fn removes_a_flag() {
        let mut perms = Permissions::all();
        perms.remove(Permissions::DELETE);
        assert!(!perms.contains(Permissions::DELETE));
        assert!(perms.contains(Permissions::READ));
    }

    #[test]
    fn empty_has_no_flags() {
        assert!(Permissions::empty().is_empty());
    }
}
