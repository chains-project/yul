use std::ffi::{CStr, CString};
use std::io;
use std::os::raw::c_char;

unsafe extern "C" {
    fn getpid() -> libc::pid_t;
    fn strlen(s: *const c_char) -> libc::size_t;
}

fn main() -> io::Result<()> {
    let pid = unsafe { getpid() };
    println!("process id: {pid}");

    let name = CString::new("native call")?;
    let len = unsafe { strlen(name.as_ptr()) };
    println!("strlen({:?}) = {len}", name);

    let uname = hostname();
    println!("hostname: {uname}");

    let path = CString::new("/tmp")?;
    let mut buf = [0u8; 64];
    let ptr = unsafe { libc::realpath(path.as_ptr(), buf.as_mut_ptr() as *mut c_char) };
    if ptr.is_null() {
        return Err(io::Error::last_os_error());
    }
    println!(
        "realpath(/tmp) = {}",
        unsafe { CStr::from_ptr(ptr) }.to_string_lossy()
    );

    Ok(())
}

fn hostname() -> String {
    let mut buf = [0u8; 256];
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr() as *mut c_char, buf.len()) };
    if rc != 0 {
        return String::from("<unknown>");
    }
    buf.iter().position(|&b| b == 0).map_or_else(
        || String::from_utf8_lossy(&buf).into_owned(),
        |end| String::from_utf8_lossy(&buf[..end]).into_owned(),
    )
}
