use std::ffi::CStr;
use std::io;

fn cstr(buf: &[libc::c_char]) -> String {
    unsafe { CStr::from_ptr(buf.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

fn hostname() -> io::Result<String> {
    let mut buf = [0 as libc::c_char; 256];
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len()) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(cstr(&buf))
}

fn uname() -> io::Result<libc::utsname> {
    let mut info: libc::utsname = unsafe { std::mem::zeroed() };
    let rc = unsafe { libc::uname(&mut info) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(info)
}

fn main() -> io::Result<()> {
    let info = uname()?;
    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: libc::uid_t = unsafe { libc::getuid() };
    let gid: libc::gid_t = unsafe { libc::getgid() };
    let page_size: libc::c_long = unsafe { libc::sysconf(libc::_SC_PAGESIZE) };
    let cpus: libc::c_long = unsafe { libc::sysconf(libc::_SC_NPROCESSORS_ONLN) };

    println!("hostname : {}", hostname()?);
    println!("sysname  : {}", cstr(&info.sysname));
    println!("release  : {}", cstr(&info.release));
    println!("machine  : {}", cstr(&info.machine));
    println!("pid      : {pid}");
    println!("uid/gid  : {uid}/{gid}");
    println!("pagesize : {page_size} bytes");
    println!("cpus     : {cpus}");
    println!(
        "stdout   : {}",
        if unsafe { libc::isatty(libc::STDOUT_FILENO) } == 1 {
            "tty"
        } else {
            "not a tty"
        }
    );

    Ok(())
}
