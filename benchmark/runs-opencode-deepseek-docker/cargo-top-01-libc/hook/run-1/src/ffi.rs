use std::os::raw::{c_char, c_int, c_long};

// Bindings for the native shim built by `build.rs` and linked as a static
// library. Signatures must stay in sync with `csrc/shim.h`.
unsafe extern "C" {
    pub fn shim_get_page_size() -> c_long;
    pub fn shim_get_uid(uid: *mut libc::uid_t) -> c_int;
    pub fn shim_to_uppercase(buf: *mut c_char, len: libc::size_t) -> libc::size_t;
}
