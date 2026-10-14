mod sys;

fn main() {
    let pid = sys::getpid();
    let uid = sys::getuid();
    println!("pid={pid} uid={uid}");

    match sys::hostname() {
        Ok(name) => println!("hostname={name}"),
        Err(e) => eprintln!("gethostname failed: {e}"),
    }

    match sys::uname() {
        Ok(u) => println!("kernel={} {} ({})", u.sysname, u.release, u.machine),
        Err(e) => eprintln!("uname failed: {e}"),
    }
}
