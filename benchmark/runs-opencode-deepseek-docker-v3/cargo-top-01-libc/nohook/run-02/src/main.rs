mod ffi;

use std::ffi::CString;
use std::io;
use std::os::unix::io::AsRawFd;

fn main() {
    let native_pid = unsafe { ffi::shim_getpid() };
    let libc_pid = unsafe { libc::getpid() };
    println!("pid via native shim: {native_pid}");
    println!("pid via libc:        {libc_pid}");
    assert_eq!(native_pid, libc_pid);

    let manifest = concat!(env!("CARGO_MANIFEST_DIR"), "/Cargo.toml");

    match file_size(manifest) {
        Ok(size) => println!("{manifest} size: {size} bytes"),
        Err(err) => eprintln!("stat failed: {err}"),
    }

    match read_prefix(manifest, 32) {
        Ok(text) => println!("{manifest} prefix: {text:?}"),
        Err(err) => eprintln!("read failed: {err}"),
    }
}

fn file_size(path: &str) -> io::Result<libc::off_t> {
    let c_path = to_cstring(path)?;
    let size = unsafe { ffi::shim_file_size(c_path.as_ptr()) };
    if size < 0 {
        Err(io::Error::last_os_error())
    } else {
        Ok(size)
    }
}

fn read_prefix(path: &str, max_len: usize) -> io::Result<String> {
    let file = std::fs::File::open(path)?;
    let mut buf = vec![0u8; max_len];
    let len = unsafe {
        ffi::shim_read_prefix(file.as_raw_fd(), buf.as_mut_ptr().cast(), buf.len())
    };
    if len < 0 {
        return Err(io::Error::last_os_error());
    }
    buf.truncate(len as usize);
    Ok(String::from_utf8_lossy(&buf).into_owned())
}

fn to_cstring(path: &str) -> io::Result<CString> {
    CString::new(path).map_err(|_| io::Error::new(io::ErrorKind::InvalidInput, "path contains NUL"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn native_pid_matches_libc() {
        assert_eq!(unsafe { ffi::shim_getpid() }, unsafe { libc::getpid() });
    }

    #[test]
    fn native_file_size_matches_std() {
        let manifest = concat!(env!("CARGO_MANIFEST_DIR"), "/Cargo.toml");
        let expected = std::fs::metadata(manifest).unwrap().len() as libc::off_t;
        assert_eq!(file_size(manifest).unwrap(), expected);
    }
}
