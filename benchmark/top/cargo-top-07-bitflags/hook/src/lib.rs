use bitflags::bitflags;

bitflags! {
    /// File-style access permissions, each represented by a single bit so
    /// they can be freely combined with `|` and tested with `contains`.
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u8 {
        const READ    = 0b0000_0001;
        const WRITE   = 0b0000_0010;
        const EXECUTE = 0b0000_0100;
    }
}

impl Permissions {
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
    fn empty_has_no_flags_set() {
        let perms = Permissions::empty();
        assert!(!perms.contains(Permissions::READ));
        assert!(!perms.contains(Permissions::WRITE));
        assert!(!perms.contains(Permissions::EXECUTE));
    }

    #[test]
    fn all_contains_every_flag() {
        let perms = Permissions::all();
        assert!(perms.contains(Permissions::READ));
        assert!(perms.contains(Permissions::WRITE));
        assert!(perms.contains(Permissions::EXECUTE));
    }
}
