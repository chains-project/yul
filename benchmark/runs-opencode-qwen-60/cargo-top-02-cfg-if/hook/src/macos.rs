pub fn platform_info() -> (&'static str, &'static str) {
    ("macOS", cfg_if::cfg_if! {
        if #[cfg(target_arch = "x86_64")] {
            "x86_64"
        } else if #[cfg(target_arch = "aarch64")] {
            "aarch64"
        } else {
            "unknown"
        }
    })
}