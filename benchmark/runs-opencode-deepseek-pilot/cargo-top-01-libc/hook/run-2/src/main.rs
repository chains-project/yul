use std::ffi::{CStr, CString};
use std::mem::MaybeUninit;

fn main() {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: libc::uid_t = unsafe { libc::getuid() };
    let gid: libc::gid_t = unsafe { libc::getgid() };

    println!("pid={pid} uid={uid} gid={gid}");

    let hostname = hostname();
    println!("hostname={hostname}");

    let mut ts = libc::timespec {
        tv_sec: 0,
        tv_nsec: 0,
    };
    let ret: libc::c_int =
        unsafe { libc::clock_gettime(libc::CLOCK_MONOTONIC, &mut ts) };
    if ret == 0 {
        println!("monotonic={}.{:09}", ts.tv_sec, ts.tv_nsec);
    }

    let cwd = std::env::current_dir().expect("cwd");
    let c_path = CString::new(cwd.as_os_str().as_encoded_bytes()).expect("cwd has no NUL");
    let ret: libc::c_int = unsafe { libc::chdir(c_path.as_ptr()) };
    if ret != 0 {
        let errno = std::io::Error::last_os_error();
        eprintln!("chdir failed: {errno}");
    }
}

fn hostname() -> String {
    let mut buf = [0i8; 256];
    let ret: libc::c_int =
        unsafe { libc::gethostname(buf.as_mut_ptr() as *mut libc::c_char, buf.len()) };
    if ret != 0 {
        return String::from("<unknown>");
    }
    let cstr = unsafe { CStr::from_ptr(buf.as_ptr() as *const libc::c_char) };
    cstr.to_string_lossy().into_owned()
}

#[allow(dead_code)]
fn uname_fields() -> (String, String, String) {
    let mut uts: libc::utsname = unsafe { MaybeUninit::zeroed().assume_init() };
    let ret: libc::c_int = unsafe { libc::uname(&mut uts) };
    if ret != 0 {
        return (String::new(), String::new(), String::new());
    }
    let conv = |p: *const libc::c_char| unsafe { CStr::from_ptr(p) }
        .to_string_lossy()
        .into_owned();
    (
        conv(uts.sysname.as_ptr()),
        conv(uts.release.as_ptr()),
        conv(uts.machine.as_ptr()),
    )
}
