use libc::{c_char, c_int, pid_t};
use std::ffi::CStr;

unsafe extern "C" {
    fn native_add(a: c_int, b: c_int) -> c_int;
    fn native_getpid() -> pid_t;
    fn native_strlen(s: *const c_char) -> usize;
}

fn main() {
    let sum = unsafe { native_add(20, 22) };
    println!("native_add(20, 22) = {sum}");

    let pid = unsafe { native_getpid() };
    println!(
        "native_getpid() = {pid} (std::process::id() = {})",
        std::process::id()
    );

    let name = c"systems_tool";
    let len = unsafe { native_strlen(name.as_ptr()) };
    println!("native_strlen({:?}) = {len}", name);

    let os = unsafe {
        let mut buf: libc::utsname = std::mem::zeroed();
        if libc::uname(&mut buf) == 0 {
            CStr::from_ptr(buf.sysname.as_ptr())
                .to_string_lossy()
                .into_owned()
        } else {
            "unknown".to_string()
        }
    };
    println!("libc::uname sysname = {os}");
}
