use std::io;

fn main() {
    let pid: libc::pid_t = unsafe { libc::getpid() };
    println!("pid = {pid}");

    let mut usage: libc::rusage = unsafe { std::mem::zeroed() };
    let ret = unsafe { libc::getrusage(libc::RUSAGE_SELF, &mut usage) };
    if ret != 0 {
        eprintln!("getrusage failed: {}", io::Error::last_os_error());
        std::process::exit(1);
    }
    println!("max resident set size = {} KB", usage.ru_maxrss);
}
