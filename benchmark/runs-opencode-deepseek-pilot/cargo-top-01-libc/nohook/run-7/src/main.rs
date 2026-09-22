use std::ffi::CStr;
use std::io;
use std::mem::MaybeUninit;

fn main() -> io::Result<()> {
    // OS-level C type: pid_t
    let pid: libc::pid_t = unsafe { libc::getpid() };
    println!("pid: {pid}");

    // OS-level C type: c_long
    let page_size: libc::c_long = unsafe { libc::sysconf(libc::_SC_PAGESIZE) };
    println!("page size: {page_size} bytes");

    // OS-level C type: utsname, filled by the native uname(2) call.
    let mut uts = MaybeUninit::<libc::utsname>::uninit();
    if unsafe { libc::uname(uts.as_mut_ptr()) } != 0 {
        return Err(io::Error::last_os_error());
    }
    let uts = unsafe { uts.assume_init() };

    // utsname fields are fixed-size [c_char; N] buffers.
    let sysname = unsafe { CStr::from_ptr(uts.sysname.as_ptr()) };
    let release = unsafe { CStr::from_ptr(uts.release.as_ptr()) };
    let machine = unsafe { CStr::from_ptr(uts.machine.as_ptr()) };

    println!("sysname: {}", sysname.to_string_lossy());
    println!("release: {}", release.to_string_lossy());
    println!("machine: {}", machine.to_string_lossy());

    Ok(())
}
