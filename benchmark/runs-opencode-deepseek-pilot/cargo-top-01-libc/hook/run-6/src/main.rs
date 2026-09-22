use std::ffi::{CStr, CString};
use std::os::raw::{c_char, c_int, c_uint};

unsafe extern "C" {
    fn fnv1a_64(data: *const u8, len: libc::size_t) -> u64;
}

fn native_checksum(data: &[u8]) -> u64 {
    unsafe { fnv1a_64(data.as_ptr(), data.len()) }
}

fn hostname() -> String {
    let mut buf = [0 as c_char; 256];
    let rc = unsafe { libc::gethostname(buf.as_mut_ptr(), buf.len()) };
    if rc != 0 {
        return "<unknown>".to_string();
    }
    unsafe { CStr::from_ptr(buf.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

fn main() {
    let payload = b"systems tooling over FFI";

    let sum = native_checksum(payload);
    println!(
        "fnv1a_64({:?}) = {:#018x}",
        String::from_utf8_lossy(payload),
        sum
    );

    let pid: libc::pid_t = unsafe { libc::getpid() };
    let uid: libc::uid_t = unsafe { libc::getuid() };
    let nproc: c_int = unsafe { libc::sysconf(libc::_SC_NPROCESSORS_ONLN) } as c_int;
    println!("pid={pid} uid={uid} cpus={nproc} host={}", hostname());

    let name = CString::new("PATH").unwrap();
    let path = unsafe { libc::getenv(name.as_ptr()) };
    if !path.is_null() {
        println!("PATH={}", unsafe { CStr::from_ptr(path) }.to_string_lossy());
    }

    let mut flags: c_uint = 0;
    flags |= libc::O_RDONLY as c_uint;
    println!("O_RDONLY flag = {flags}");
}
