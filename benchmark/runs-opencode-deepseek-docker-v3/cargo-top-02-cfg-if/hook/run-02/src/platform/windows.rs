use super::Platform;

/// Microsoft Windows.
pub struct Windows;

impl Platform for Windows {
    const NAME: &'static str = "windows";

    fn page_size() -> usize {
        // The default page size on all currently supported Windows versions.
        // Swap in `GetSystemInfo` (from `windows-sys`) here if you need the
        // value reported by the running system.
        4096
    }

    fn max_threads() -> usize {
        std::thread::available_parallelism().map_or(1, std::num::NonZero::get)
    }
}
