use libc::{c_char, c_int, off_t, pid_t, size_t, ssize_t};

unsafe extern "C" {
    pub fn shim_getpid() -> pid_t;
    pub fn shim_file_size(path: *const c_char) -> off_t;
    pub fn shim_read_prefix(fd: c_int, buf: *mut c_char, len: size_t) -> ssize_t;
}
