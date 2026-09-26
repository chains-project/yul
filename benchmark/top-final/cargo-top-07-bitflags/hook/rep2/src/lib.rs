use bitflags::bitflags;

bitflags! {
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u32 {
        const READ    = 0b0000_0001;
        const WRITE   = 0b0000_0010;
        const EXECUTE = 0b0000_0100;
        const DELETE  = 0b0000_1000;
    }
}

impl Permissions {
    pub fn readonly() -> Self {
        Permissions::READ
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
    fn readonly_is_read_only() {
        let perms = Permissions::readonly();
        assert_eq!(perms, Permissions::READ);
    }

    #[test]
    fn remove_flag() {
        let mut perms = Permissions::READ | Permissions::WRITE | Permissions::EXECUTE;
        perms.remove(Permissions::EXECUTE);
        assert!(!perms.contains(Permissions::EXECUTE));
        assert!(perms.contains(Permissions::READ | Permissions::WRITE));
    }
}
