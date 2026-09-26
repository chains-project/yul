use std::ffi::CString;
use std::io;

fn main() {
    // pid_t, uid_t, gid_t are OS-level C types re-exported by `libc`
    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: libc::uid_t = unsafe { libc::getuid() };
    let gid: libc::gid_t = unsafe { libc::getgid() };

    println!("pid={pid} uid={uid} gid={gid}");

    // Round-trip a hostname through the C API using a raw buffer.
    let mut buf = [0u8; 256];
    let ret = unsafe {
        libc::gethostname(buf.as_mut_ptr() as *mut libc::c_char, buf.len())
    };
    if ret == 0 {
        let hostname = unsafe { CString::from_vec_unchecked(
            buf.iter().take_while(|&&b| b != 0).cloned().collect(),
        ) };
        println!("hostname={}", hostname.to_string_lossy());
    } else {
        eprintln!("gethostname failed: {}", io::Error::last_os_error());
    }
}
