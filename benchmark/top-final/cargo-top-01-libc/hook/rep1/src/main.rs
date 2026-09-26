use libc::{c_int, getpid, getuid, pid_t, uid_t};

fn main() {
    let pid: pid_t = unsafe { getpid() };
    let uid: uid_t = unsafe { getuid() };
    let page_size: c_int = unsafe { libc::sysconf(libc::_SC_PAGESIZE) as c_int };

    println!("pid={pid} uid={uid} page_size={page_size}");
}
