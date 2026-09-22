use std::mem::MaybeUninit;

fn main() {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: libc::uid_t = unsafe { libc::getuid() };
    println!("pid={pid} uid={uid}");

    let mut uts = MaybeUninit::<libc::utsname>::uninit();
    let rc: libc::c_int = unsafe { libc::uname(uts.as_mut_ptr()) };
    if rc == 0 {
        let uts = unsafe { uts.assume_init() };
        let sysname = unsafe { std::ffi::CStr::from_ptr(uts.sysname.as_ptr()) };
        println!("sysname={}", sysname.to_string_lossy());
    }
}
