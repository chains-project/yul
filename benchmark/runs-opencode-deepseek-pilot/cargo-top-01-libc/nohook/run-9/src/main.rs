use std::ffi::CStr;
use std::io;

fn c_char_array_to_string(buf: &[libc::c_char]) -> String {
    unsafe { CStr::from_ptr(buf.as_ptr()).to_string_lossy().into_owned() }
}

fn process_ids() -> (libc::pid_t, libc::uid_t, libc::gid_t) {
    unsafe { (libc::getpid(), libc::getuid(), libc::getgid()) }
}

fn system_name() -> io::Result<String> {
    let mut uts: libc::utsname = unsafe { std::mem::zeroed() };

    let rc = unsafe { libc::uname(&mut uts) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }

    Ok(format!(
        "{} {} {}",
        c_char_array_to_string(&uts.sysname),
        c_char_array_to_string(&uts.release),
        c_char_array_to_string(&uts.machine),
    ))
}

fn monotonic_clock() -> io::Result<libc::timespec> {
    let mut ts: libc::timespec = unsafe { std::mem::zeroed() };

    let rc = unsafe { libc::clock_gettime(libc::CLOCK_MONOTONIC, &mut ts) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }

    Ok(ts)
}

fn write_all(fd: libc::c_int, data: &[u8]) -> io::Result<()> {
    let mut written = 0usize;
    while written < data.len() {
        let rc = unsafe {
            libc::write(
                fd,
                data[written..].as_ptr().cast::<libc::c_void>(),
                data.len() - written,
            )
        };

        if rc < 0 {
            return Err(io::Error::last_os_error());
        }
        written += rc as usize;
    }

    Ok(())
}

fn main() -> io::Result<()> {
    let (pid, uid, gid) = process_ids();
    let uname = system_name()?;
    let ts = monotonic_clock()?;

    let report = format!(
        "pid={pid} uid={uid} gid={gid}\nuname={uname}\nmonotonic={}.{:09}\n",
        ts.tv_sec, ts.tv_nsec
    );

    write_all(libc::STDOUT_FILENO, report.as_bytes())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pid_is_positive() {
        let (pid, _, _) = process_ids();
        assert!(pid > 0);
    }

    #[test]
    fn uname_is_not_empty() {
        let name = system_name().expect("uname failed");
        assert!(!name.trim().is_empty());
    }

    #[test]
    fn monotonic_clock_advances() {
        let first = monotonic_clock().expect("clock_gettime failed");
        let second = monotonic_clock().expect("clock_gettime failed");
        let elapsed = (second.tv_sec, second.tv_nsec) >= (first.tv_sec, first.tv_nsec);
        assert!(elapsed);
    }
}
