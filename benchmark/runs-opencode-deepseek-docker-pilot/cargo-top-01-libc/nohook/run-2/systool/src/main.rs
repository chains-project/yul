use std::ffi::{CStr, CString};
use std::mem::MaybeUninit;
use std::process::ExitCode;

use libc::{c_char, c_int, c_long, pid_t, uid_t, utsname};

extern "C" {
    fn getpid() -> pid_t;
    fn getuid() -> uid_t;
    fn sysconf(name: c_int) -> c_long;
    fn uname(buf: *mut utsname) -> c_int;
    fn chdir(path: *const c_char) -> c_int;
    fn strerror(errnum: c_int) -> *mut c_char;
}

fn c_field(buf: &[c_char]) -> String {
    unsafe { CStr::from_ptr(buf.as_ptr()) }
        .to_string_lossy()
        .into_owned()
}

fn main() -> ExitCode {
    let pid = unsafe { getpid() };
    let uid = unsafe { getuid() };
    let page_size = unsafe { sysconf(libc::_SC_PAGESIZE) };
    let clk_tck = unsafe { sysconf(libc::_SC_CLK_TCK) };

    println!("pid       = {pid}");
    println!("uid       = {uid}");
    println!("page_size = {page_size}");
    println!("clk_tck   = {clk_tck}");

    let mut info = MaybeUninit::<utsname>::uninit();
    if unsafe { uname(info.as_mut_ptr()) } == 0 {
        let info = unsafe { info.assume_init() };
        println!("sysname   = {}", c_field(&info.sysname));
        println!("nodename  = {}", c_field(&info.nodename));
        println!("release   = {}", c_field(&info.release));
        println!("machine   = {}", c_field(&info.machine));
    } else {
        eprintln!("uname failed");
        return ExitCode::FAILURE;
    }

    let missing = CString::new("/this/path/does/not/exist").expect("no NUL");
    if unsafe { chdir(missing.as_ptr()) } != 0 {
        let err = std::io::Error::last_os_error();
        let code = err.raw_os_error().unwrap_or(0);
        let msg = unsafe { CStr::from_ptr(strerror(code)) }.to_string_lossy();
        println!("chdir errno = {code} ({msg})");
    }

    ExitCode::SUCCESS
}
