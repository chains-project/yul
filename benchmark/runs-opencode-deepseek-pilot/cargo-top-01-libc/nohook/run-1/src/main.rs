use std::io;

fn process_id() -> libc::pid_t {
    unsafe { libc::getpid() }
}

fn user_id() -> libc::uid_t {
    unsafe { libc::getuid() }
}

fn write_stdout(buf: &[u8]) -> io::Result<libc::ssize_t> {
    let written: libc::ssize_t = unsafe {
        libc::write(
            libc::STDOUT_FILENO,
            buf.as_ptr() as *const libc::c_void,
            buf.len() as libc::size_t,
        )
    };

    if written < 0 {
        Err(io::Error::last_os_error())
    } else {
        Ok(written)
    }
}

fn main() {
    let pid: libc::pid_t = process_id();
    let uid: libc::uid_t = user_id();
    let message = format!("pid={pid} uid={uid}\n");

    match write_stdout(message.as_bytes()) {
        Ok(_n) => {}
        Err(err) => eprintln!("write failed: {err}"),
    }
}
