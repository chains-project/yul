use std::ffi::CStr;

unsafe extern "C" {
    fn strlen(s: *const libc::c_char) -> libc::size_t;
}

pub fn c_strlen(s: &CStr) -> usize {
    unsafe { strlen(s.as_ptr()) }
}

pub fn pid() -> libc::pid_t {
    unsafe { libc::getpid() }
}
