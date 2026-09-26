use std::ffi::CString;

fn main() {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    println!("pid: {}", pid);

    let path = CString::new(".").unwrap();
    let mode = libc::F_OK;
    let accessible = unsafe { libc::access(path.as_ptr(), mode) } == 0;
    println!("current dir accessible: {}", accessible);
}
