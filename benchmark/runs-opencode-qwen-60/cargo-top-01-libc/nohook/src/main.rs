use libc::{c_int, c_char, size_t, pid_t, off_t, time_t, mode_t, uid_t, gid_t};
use libc::{stat as c_stat, open as c_open, O_RDONLY};

extern "C" {
    fn perror(msg: *const c_char);
    fn printf(format: *const c_char, ...) -> c_int;
}

fn main() {
    println!("C library types demo:");

    let _pid: pid_t = unsafe { libc::getpid() };
    let _uid: uid_t = unsafe { libc::geteuid() };
    let _gid: gid_t = unsafe { libc::getegid() };

    println!("  pid_t, uid_t, gid_t available");

    // Use libc::stat to demonstrate struct bindings
    let path = b"/tmp\0";
    let mut st: c_stat = unsafe { std::mem::zeroed() };
    let ret = unsafe { c_stat(path.as_ptr(), &mut st as *mut c_stat) };
    if ret == 0 {
        unsafe {
            printf(b"stat: st_mode=%o st_size=%lld st_mtime=%lld\0"
                .as_ptr() as *const c_char,
                st.st_mode as libc::c_ulonglong,
                st.st_size as libc::c_longlong,
                st.st_mtime as libc::c_longlong,
            );
        }
    }

    println!();
    println!("Supported C types via libc crate:");
    println!("  c_int, c_char, size_t, pid_t");
    println!("  off_t, time_t, mode_t, uid_t, gid_t");
    println!("  stat, dirent, sockaddr, etc.");
}