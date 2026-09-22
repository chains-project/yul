use std::ffi::CStr;

use libc::{c_char, pid_t, uid_t};

fn hostname() -> String {
    let mut buf = [0 as c_char; 256];
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len()) };
    if rc != 0 {
        return String::from("<unknown>");
    }
    unsafe { CStr::from_ptr(buf.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

fn main() {
    let pid: pid_t = unsafe { libc::getpid() };
    let uid: uid_t = unsafe { libc::getuid() };

    println!("pid:      {pid}");
    println!("uid:      {uid}");
    println!("hostname: {}", hostname());
}
