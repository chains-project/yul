use std::ffi::CStr;

fn main() {
    unsafe {
        let pid: libc::pid_t = libc::getpid();
        let uid: libc::uid_t = libc::getuid();
        let gid: libc::gid_t = libc::getgid();

        println!("pid  = {pid}");
        println!("uid  = {uid}");
        println!("gid  = {gid}");

        let mut hostname = [0 as libc::c_char; 256];
        let rc: libc::c_int = libc::gethostname(hostname.as_mut_ptr(), hostname.len());
        if rc == 0 {
            let name = CStr::from_ptr(hostname.as_ptr());
            println!("host = {}", name.to_string_lossy());
        } else {
            eprintln!("gethostname failed: {}", std::io::Error::last_os_error());
            std::process::exit(libc::EXIT_FAILURE);
        }
    }
}
