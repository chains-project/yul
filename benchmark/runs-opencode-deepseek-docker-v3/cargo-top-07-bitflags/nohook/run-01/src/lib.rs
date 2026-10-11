use bitflags::bitflags;

bitflags! {
    #[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
    pub struct Flags: u32 {
        const A = 0b0000_0001;
        const B = 0b0000_0010;
        const C = 0b0000_0100;
        const D = 0b0000_1000;
        const AB = Self::A.bits() | Self::B.bits();
        const ALL = Self::A.bits() | Self::B.bits() | Self::C.bits() | Self::D.bits();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn combine_and_check() {
        let flags = Flags::A | Flags::B;
        assert!(flags.contains(Flags::A));
        assert!(flags.contains(Flags::B));
        assert!(!flags.contains(Flags::C));
        assert_eq!(flags, Flags::AB);
    }

    #[test]
    fn insert_and_remove() {
        let mut flags = Flags::A;
        flags.insert(Flags::C);
        assert_eq!(flags, Flags::A | Flags::C);
        flags.remove(Flags::A);
        assert!(flags.contains(Flags::C));
        assert!(!flags.contains(Flags::A));
    }

    #[test]
    fn all_contains_every_bit() {
        assert!(Flags::ALL.contains(Flags::A | Flags::B | Flags::C | Flags::D));
    }
}
