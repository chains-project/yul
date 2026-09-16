use bitflags::bitflags;

bitflags! {
    pub struct Permissions: u32 {
        const READ    = 1 << 0;
        const WRITE   = 1 << 1;
        const EXECUTE = 1 << 2;
        const DELETE  = 1 << 3;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn single_flag() {
        let perms = Permissions::READ;
        assert!(perms.contains(Permissions::READ));
        assert!(!perms.contains(Permissions::WRITE));
    }

    #[test]
    fn combined_flags() {
        let perms = Permissions::READ | Permissions::WRITE;
        assert!(perms.contains(Permissions::READ | Permissions::WRITE));
        assert!(!perms.contains(Permissions::EXECUTE));
    }

    #[test]
    fn all_flags() {
        let perms = Permissions::all();
        assert!(perms.contains(Permissions::READ | Permissions::WRITE | Permissions::EXECUTE | Permissions::DELETE));
    }

    #[test]
    fn removing_flags() {
        let perms = Permissions::READ | Permissions::WRITE;
        let perms = perms - Permissions::READ;
        assert!(!perms.contains(Permissions::READ));
        assert!(perms.contains(Permissions::WRITE));
    }
}