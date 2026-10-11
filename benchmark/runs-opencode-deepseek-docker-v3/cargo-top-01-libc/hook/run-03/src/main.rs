mod ffi;

use libc::{getpid, pid_t};

fn main() {
    let values = [10_i64, 20, 30, 40];

    println!("sum (via C)    = {}", ffi::sum(&values));

    let stats = ffi::collect(&values);
    println!(
        "stats (via C)  = count={}, total={}",
        stats.count, stats.total
    );

    let c_pid: pid_t = ffi::pid();
    println!("pid (via C)    = {c_pid}");

    let libc_pid: pid_t = unsafe { getpid() };
    println!("pid (via libc) = {libc_pid}");
}
