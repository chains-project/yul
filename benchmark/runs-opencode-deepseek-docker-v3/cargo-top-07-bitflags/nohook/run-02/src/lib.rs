use bitflags::bitflags;

bitflags! {
    /// Type-safe bit flags that can be combined with `|` and tested with
    /// [`Flags::contains`].
    #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
    pub struct Flags: u32 {
        const READ    = 0b0000_0001;
        const WRITE   = 0b0000_0010;
        const EXECUTE = 0b0000_0100;
        const ALL     = Self::READ.bits() | Self::WRITE.bits() | Self::EXECUTE.bits();
    }
}

impl Flags {
    /// Returns `true` if every flag in `other` is set on `self`.
    pub fn has(self, other: Flags) -> bool {
        self.contains(other)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combines_flags() {
        let rw = Flags::READ | Flags::WRITE;
        assert!(rw.contains(Flags::READ));
        assert!(rw.contains(Flags::WRITE));
        assert!(!rw.contains(Flags::EXECUTE));
    }

    #[test]
    fn has_checks_all_flags() {
        let all = Flags::ALL;
        assert!(all.has(Flags::READ | Flags::WRITE | Flags::EXECUTE));
    }

    #[test]
    fn empty_contains_nothing() {
        assert!(!Flags::empty().contains(Flags::READ));
        assert!(Flags::empty().is_empty());
    }
}
