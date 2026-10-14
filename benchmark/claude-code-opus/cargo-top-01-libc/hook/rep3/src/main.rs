//! systool: a systems utility built on native C library calls via `libc`.

mod sys;

fn main() {
    let pid = sys::getpid();
    println!("pid: {pid}");

    match sys::hostname() {
        Ok(name) => println!("hostname: {name}"),
        Err(e) => eprintln!("hostname: {e}"),
    }

    match sys::uname() {
        Ok(u) => println!("kernel: {} {} ({})", u.sysname, u.release, u.machine),
        Err(e) => eprintln!("uname: {e}"),
    }
}
