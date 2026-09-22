use libc::{c_char, c_int, c_long, uid_t};
use std::ffi::CStr;
use std::mem::MaybeUninit;

fn hostname() -> String {
    let mut buf = [0 as c_char; 256];
    let rc: c_int = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len()) };
    if rc != 0 {
        return String::from("<unknown>");
    }
    unsafe { CStr::from_ptr(buf.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

fn uname_release() -> String {
    let mut info = MaybeUninit::<libc::utsname>::uninit();
    let rc: c_int = unsafe { libc::uname(info.as_mut_ptr()) };
    if rc != 0 {
        return String::from("<unknown>");
    }
    let info = unsafe { info.assume_init() };
    unsafe { CStr::from_ptr(info.release.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

fn main() {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: uid_t = unsafe { libc::getuid() };
    let ncpus: c_long = unsafe { libc::sysconf(libc::_SC_NPROCESSORS_ONLN) };

    println!("pid:        {pid}");
    println!("uid:        {uid}");
    println!("cpus:       {ncpus}");
    println!("hostname:   {}", hostname());
    println!("kernel:     {}", uname_release());
}
