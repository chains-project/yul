use bitflags::bitflags;

// Define a type-safe set of bitflag constants that can be combined and checked.
// This example demonstrates file attribute flags, but the pattern works for any
// domain where you need to represent multiple boolean options efficiently.

bitflags! {
    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    pub struct FileAttributes: u32 {
        const READ = 0x1;
        const WRITE = 0x2;
        const EXECUTE = 0x4;
        const HIDDEN = 0x8;
        const SYSTEM = 0x10;
        const ARCHIVE = 0x20;
        const DIRECTORY = 0x40;
    }
}

// Demonstrate usage in a simple context
impl FileAttributes {
    /// Returns true if the file has both read and write permissions.
    pub fn is_writable(&self) -> bool {
        self.contains(FileAttributes::READ | FileAttributes::WRITE)
    }

    /// Returns true if the file is executable.
    pub fn is_executable(&self) -> bool {
        self.contains(FileAttributes::EXECUTE)
    }

    /// Returns true if the file is visible (not hidden).
    pub fn is_visible(&self) -> bool {
        !self.contains(FileAttributes::HIDDEN)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_combining_flags() {
        let attrs = FileAttributes::READ | FileAttributes::WRITE;
        assert!(attrs.contains(FileAttributes::READ));
        assert!(attrs.contains(FileAttributes::WRITE));
        assert!(!attrs.contains(FileAttributes::EXECUTE));
    }

    #[test]
    fn test_checking_flags() {
        let attrs = FileAttributes::READ | FileAttributes::WRITE | FileAttributes::EXECUTE;
        assert!(attrs.is_writable());
        assert!(attrs.is_executable());
        assert!(attrs.is_visible());
    }

    #[test]
    fn test_removing_flags() {
        let mut attrs = FileAttributes::READ | FileAttributes::WRITE | FileAttributes::EXECUTE;
        attrs.remove(FileAttributes::WRITE);
        assert!(attrs.contains(FileAttributes::READ));
        assert!(!attrs.contains(FileAttributes::WRITE));
    }

    #[test]
    fn test_empty_flags() {
        let empty = FileAttributes::empty();
        assert!(!empty.contains(FileAttributes::READ));
        assert!(!empty.is_writable());
        assert!(empty.is_visible());
    }

    #[test]
    fn test_all_flags() {
        let all = FileAttributes::all();
        assert!(all.contains(FileAttributes::READ));
        assert!(all.contains(FileAttributes::WRITE));
        assert!(all.contains(FileAttributes::EXECUTE));
        assert!(all.contains(FileAttributes::HIDDEN));
        assert!(all.contains(FileAttributes::SYSTEM));
        assert!(all.contains(FileAttributes::ARCHIVE));
        assert!(all.contains(FileAttributes::DIRECTORY));
    }

    #[test]
    fn test_intersects() {
        let attrs = FileAttributes::READ | FileAttributes::WRITE;
        assert!(attrs.intersects(FileAttributes::READ));
        assert!(attrs.intersects(FileAttributes::WRITE | FileAttributes::EXECUTE));
        assert!(!attrs.intersects(FileAttributes::EXECUTE));
    }

    #[test]
    fn test_contains_exact() {
        let attrs = FileAttributes::READ | FileAttributes::WRITE;
        assert!(attrs.contains(FileAttributes::READ));
        assert!(attrs.contains(FileAttributes::READ | FileAttributes::WRITE));
        assert!(!attrs.contains(FileAttributes::READ | FileAttributes::WRITE | FileAttributes::EXECUTE));
    }

    #[test]
    fn test_iterator() {
        let attrs = FileAttributes::READ | FileAttributes::WRITE;
        let flags: Vec<_> = attrs.iter().collect();
        assert_eq!(flags.len(), 2);
        assert!(flags.contains(&FileAttributes::READ));
        assert!(flags.contains(&FileAttributes::WRITE));
    }

    #[test]
    fn test_formatting() {
        let attrs = FileAttributes::READ | FileAttributes::EXECUTE;
        assert_eq!(format!("{:?}", attrs), "FileAttributes(READ | EXECUTE)");
    }
}