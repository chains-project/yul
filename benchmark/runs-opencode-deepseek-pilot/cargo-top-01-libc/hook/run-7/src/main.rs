use std::ffi::CStr;
use std::mem::MaybeUninit;

use libc::{c_char, pid_t, uid_t};

fn process_id() -> pid_t {
    unsafe { libc::getpid() }
}

fn user_id() -> uid_t {
    unsafe { libc::getuid() }
}

fn hostname() -> String {
    let mut buf = [0 as c_char; 256];
    unsafe {
        if libc::gethostname(buf.as_mut_ptr(), buf.len()) != 0 {
            return String::from("<unknown>");
        }
    }
    unsafe { CStr::from_ptr(buf.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

fn system_name() -> String {
    let mut info = MaybeUninit::<libc::utsname>::uninit();
    let info = unsafe {
        if libc::uname(info.as_mut_ptr()) != 0 {
            return String::from("<unknown>");
        }
        info.assume_init()
    };
    let bytes: Vec<u8> = info
        .sysname
        .iter()
        .take_while(|&&c| c != 0)
        .map(|&c| c as u8)
        .collect();
    String::from_utf8_lossy(&bytes).into_owned()
}

fn main() {
    println!("pid: {}", process_id());
    println!("uid: {}", user_id());
    println!("hostname: {}", hostname());
    println!("sysname: {}", system_name());
}
