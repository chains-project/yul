mod sys;

use std::io;

fn main() -> io::Result<()> {
    let uts = sys::uname()?;
    println!("host:    {}", sys::hostname()?);
    println!("kernel:  {} {} ({})", uts.sysname, uts.release, uts.machine);
    println!("pid:     {}", sys::pid());
    println!("uid:     {}", sys::uid());

    let (total, avail) = sys::fs_space("/")?;
    println!("rootfs:  {} MiB free of {} MiB", avail >> 20, total >> 20);
    Ok(())
}
