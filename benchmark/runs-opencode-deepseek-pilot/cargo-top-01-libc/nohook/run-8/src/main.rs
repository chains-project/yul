use std::ffi::CStr;
use std::io;

fn hostname() -> io::Result<String> {
    let mut buf = [0 as libc::c_char; 256];
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len()) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    let cstr = unsafe { CStr::from_ptr(buf.as_ptr()) };
    Ok(cstr.to_string_lossy().into_owned())
}

fn uname() -> io::Result<libc::utsname> {
    let mut info: libc::utsname = unsafe { std::mem::zeroed() };
    let rc = unsafe { libc::uname(&mut info) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(info)
}

fn main() {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: libc::uid_t = unsafe { libc::getuid() };
    let gid: libc::gid_t = unsafe { libc::getgid() };

    println!("pid: {pid} (uid={uid}, gid={gid})");

    match hostname() {
        Ok(name) => println!("hostname: {name}"),
        Err(e) => eprintln!("gethostname failed: {e}"),
    }

    match uname() {
        Ok(info) => {
            let sysname = unsafe { CStr::from_ptr(info.sysname.as_ptr()) };
            let release = unsafe { CStr::from_ptr(info.release.as_ptr()) };
            let machine = unsafe { CStr::from_ptr(info.machine.as_ptr()) };
            println!(
                "uname: {} {} ({})",
                sysname.to_string_lossy(),
                release.to_string_lossy(),
                machine.to_string_lossy()
            );
        }
        Err(e) => eprintln!("uname failed: {e}"),
    }

    let stdout_is_tty: libc::c_int = unsafe { libc::isatty(libc::STDOUT_FILENO) };
    println!("stdout is a tty: {}", stdout_is_tty == 1);
}
