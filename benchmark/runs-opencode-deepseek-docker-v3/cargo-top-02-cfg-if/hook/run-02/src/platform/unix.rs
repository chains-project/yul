use super::Platform;

/// Unix-family platforms: Linux, macOS, the BSDs, and friends.
pub struct Unix;

impl Platform for Unix {
    const NAME: &'static str = "unix";

    fn page_size() -> usize {
        // SAFETY: `sysconf` with `_SC_PAGESIZE` has no preconditions and does
        // not touch memory; it only reads a kernel-provided constant.
        #[allow(unsafe_code)]
        let page_size = unsafe { libc::sysconf(libc::_SC_PAGESIZE) };

        usize::try_from(page_size).unwrap_or(4096)
    }

    fn max_threads() -> usize {
        std::thread::available_parallelism().map_or(1, std::num::NonZero::get)
    }
}
