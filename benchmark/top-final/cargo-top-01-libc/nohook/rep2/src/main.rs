use std::io;

fn getpid() -> libc::pid_t {
    unsafe { libc::getpid() }
}

fn hostname() -> io::Result<String> {
    let mut buf = vec![0u8; 256];
    let ret = unsafe { libc::gethostname(buf.as_mut_ptr() as *mut libc::c_char, buf.len()) };
    if ret != 0 {
        return Err(io::Error::last_os_error());
    }
    let len = buf.iter().position(|&b| b == 0).unwrap_or(buf.len());
    Ok(String::from_utf8_lossy(&buf[..len]).into_owned())
}

fn uptime_seconds() -> io::Result<i64> {
    let mut info: libc::sysinfo = unsafe { std::mem::zeroed() };
    let ret = unsafe { libc::sysinfo(&mut info) };
    if ret != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(info.uptime as i64)
}

fn main() {
    println!("pid: {}", getpid());

    match hostname() {
        Ok(name) => println!("hostname: {name}"),
        Err(e) => eprintln!("gethostname failed: {e}"),
    }

    match uptime_seconds() {
        Ok(secs) => println!("uptime: {secs}s"),
        Err(e) => eprintln!("sysinfo failed: {e}"),
    }
}
