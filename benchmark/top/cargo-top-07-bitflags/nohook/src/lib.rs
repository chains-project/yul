use bitflags::bitflags;

bitflags! {
    /// A type-safe set of file permission flags that can be combined and checked.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u8 {
        const READ    = 0b0000_0001;
        const WRITE   = 0b0000_0010;
        const EXECUTE = 0b0000_0100;
        const DELETE  = 0b0000_1000;
    }
}

impl Permissions {
    /// Shorthand for the common "read + write" combination.
    pub const READ_WRITE: Self = Self::READ.union(Self::WRITE);
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
    fn named_combination_matches_manual_union() {
        assert_eq!(Permissions::READ_WRITE, Permissions::READ | Permissions::WRITE);
    }

    #[test]
    fn removes_a_flag() {
        let mut perms = Permissions::READ | Permissions::WRITE | Permissions::EXECUTE;
        perms.remove(Permissions::WRITE);
        assert!(!perms.contains(Permissions::WRITE));
        assert!(perms.contains(Permissions::READ));
        assert!(perms.contains(Permissions::EXECUTE));
    }

    #[test]
    fn empty_and_all_behave_as_expected() {
        assert!(Permissions::empty().is_empty());
        assert!(Permissions::all().contains(Permissions::DELETE));
    }
}
