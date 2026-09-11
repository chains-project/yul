use bitflags::bitflags;

bitflags! {
    /// A type-safe set of permission flags that can be combined and checked.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
    pub struct Permissions: u32 {
        const READ    = 1 << 0;
        const WRITE   = 1 << 1;
        const EXECUTE = 1 << 2;
        const DELETE  = 1 << 3;
    }
}

impl Permissions {
    /// Convenience constant combining the common read/write permissions.
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
    fn named_combination_matches_bitor() {
        assert_eq!(Permissions::READ_WRITE, Permissions::READ | Permissions::WRITE);
    }

    #[test]
    fn empty_and_all() {
        assert!(Permissions::empty().is_empty());
        assert!(Permissions::all().contains(Permissions::DELETE));
    }

    #[test]
    fn remove_flag() {
        let mut perms = Permissions::all();
        perms.remove(Permissions::EXECUTE);
        assert!(!perms.contains(Permissions::EXECUTE));
        assert!(perms.contains(Permissions::READ));
    }
}
