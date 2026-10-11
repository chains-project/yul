use std::ffi::{CStr, c_void};
use std::io::Write;
use std::os::raw::{c_char, c_int, c_long};

unsafe extern "C" {
    fn helper_page_size() -> c_long;
    fn helper_platform() -> *const c_char;
    fn helper_write_all(fd: c_int, buf: *const c_void, count: usize) -> isize;
}

fn main() {
    unsafe {
        let platform = CStr::from_ptr(helper_platform());
        let page_size = helper_page_size();
        println!("platform:  {}", platform.to_string_lossy());
        println!("page size: {page_size}");

        let msg = b"written via the bundled C library\n";
        let written = helper_write_all(libc::STDOUT_FILENO, msg.as_ptr().cast(), msg.len());
        assert_eq!(written as usize, msg.len());

        let pid = libc::getpid();
        let uid = libc::getuid();
        println!("pid:       {pid}");
        println!("uid:       {uid}");
    }

    std::io::stdout().flush().unwrap();
}
