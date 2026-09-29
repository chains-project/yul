use bitflags::bitflags;

bitflags! {
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Permissions: u32 {
        const READ = 0b0000_0001;
        const WRITE = 0b0000_0010;
        const EXECUTE = 0b0000_0100;
        const READ_WRITE = Self::READ.bits() | Self::WRITE.bits();
        const ALL = Self::READ.bits() | Self::WRITE.bits() | Self::EXECUTE.bits();
    }
}

impl Permissions {
    pub fn readable(self) -> bool {
        self.contains(Self::READ)
    }

    pub fn writable(self) -> bool {
        self.contains(Self::WRITE)
    }

    pub fn executable(self) -> bool {
        self.contains(Self::EXECUTE)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn constants_are_combinable() {
        let rw = Permissions::READ | Permissions::WRITE;
        assert_eq!(rw, Permissions::READ_WRITE);
    }

    #[test]
    fn combined_flags_can_be_checked() {
        let perms = Permissions::READ | Permissions::EXECUTE;
        assert!(perms.readable());
        assert!(!perms.writable());
        assert!(perms.executable());
        assert!(perms.contains(Permissions::READ));
        assert!(perms.contains(Permissions::READ | Permissions::EXECUTE));
        assert!(!perms.contains(Permissions::WRITE));
    }

    #[test]
    fn flags_can_be_mutated() {
        let mut perms = Permissions::READ;
        assert!(!perms.writable());

        perms.insert(Permissions::WRITE);
        assert!(perms.writable());

        perms.remove(Permissions::READ);
        assert!(!perms.readable());

        perms.toggle(Permissions::EXECUTE);
        assert!(perms.executable());
    }

    #[test]
    fn all_and_empty_behave_as_expected() {
        assert!(Permissions::ALL.contains(Permissions::READ_WRITE));
        assert!(!Permissions::empty().contains(Permissions::READ));
    }
}
