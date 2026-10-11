mod ffi;

use std::ffi::CString;
use std::io;

fn main() -> io::Result<()> {
    let info = ffi::proc_info()?;
    println!("native pid       = {}", info.pid);
    println!("native uid/gid   = {}/{}", info.uid, info.gid);
    println!("native page size = {}", info.page_size);

    let libc_pid = unsafe { libc::getpid() };
    let libc_pagesize = unsafe { libc::sysconf(libc::_SC_PAGESIZE) };
    println!("libc   pid       = {}", libc_pid);
    println!("libc   page size = {}", libc_pagesize);
    println!("ffi    page size = {}", ffi::page_size());

    let path = CString::new("/etc/hostname").expect("path has no interior nul");
    let (dev, ino) = ffi::file_dev_ino(&path)?;
    println!("/etc/hostname dev={dev} ino={ino}");

    Ok(())
}
