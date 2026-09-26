use std::ffi::CString;

fn main() {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    println!("pid = {pid}");

    let hostname = get_hostname().unwrap_or_else(|| "<unknown>".to_string());
    println!("hostname = {hostname}");

    let path = CString::new("/tmp").unwrap();
    let mut stat: libc::stat = unsafe { std::mem::zeroed() };
    let rc = unsafe { libc::stat(path.as_ptr(), &mut stat) };
    if rc == 0 {
        println!("/tmp size = {} bytes, mode = {:o}", stat.st_size, stat.st_mode);
    } else {
        eprintln!("stat failed: {}", std::io::Error::last_os_error());
    }
}

fn get_hostname() -> Option<String> {
    let mut buf = vec![0u8; 256];
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr() as *mut libc::c_char, buf.len()) };
    if rc != 0 {
        return None;
    }
    let end = buf.iter().position(|&b| b == 0).unwrap_or(buf.len());
    Some(String::from_utf8_lossy(&buf[..end]).into_owned())
}
