use std::ffi::CStr;
use std::io;

fn pid() -> libc::pid_t {
    unsafe { libc::getpid() }
}

fn parent_pid() -> libc::pid_t {
    unsafe { libc::getppid() }
}

fn uid() -> libc::uid_t {
    unsafe { libc::getuid() }
}

fn gid() -> libc::gid_t {
    unsafe { libc::getgid() }
}

fn page_size() -> libc::c_long {
    unsafe { libc::sysconf(libc::_SC_PAGESIZE) }
}

fn hostname() -> io::Result<String> {
    let mut buf = [0 as libc::c_char; 256];
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len()) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(c_array_to_string(&buf))
}

fn uname() -> io::Result<libc::utsname> {
    let mut info: libc::utsname = unsafe { std::mem::zeroed() };
    let rc = unsafe { libc::uname(&mut info) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(info)
}

fn c_array_to_string(buf: &[libc::c_char]) -> String {
    let cstr = unsafe { CStr::from_ptr(buf.as_ptr()) };
    cstr.to_string_lossy().into_owned()
}

fn main() -> io::Result<()> {
    println!("pid          = {}", pid());
    println!("parent pid   = {}", parent_pid());
    println!("uid / gid    = {} / {}", uid(), gid());
    println!("page size    = {} bytes", page_size());
    println!("hostname     = {}", hostname()?);

    let info = uname()?;
    println!("sysname      = {}", c_array_to_string(&info.sysname));
    println!("nodename     = {}", c_array_to_string(&info.nodename));
    println!("release      = {}", c_array_to_string(&info.release));
    println!("version      = {}", c_array_to_string(&info.version));
    println!("machine      = {}", c_array_to_string(&info.machine));

    Ok(())
}
