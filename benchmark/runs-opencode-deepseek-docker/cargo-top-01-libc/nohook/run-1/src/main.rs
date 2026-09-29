use std::process::ExitCode;

use sys_tool::ffi;

fn main() -> ExitCode {
    println!("pid:      {}", ffi::pid());
    println!("ppid:     {}", ffi::parent_pid());
    println!("uid/gid:  {}/{}", ffi::uid(), ffi::gid());

    match ffi::hostname() {
        Ok(name) => println!("hostname: {name}"),
        Err(err) => eprintln!("hostname: error: {err}"),
    }

    match ffi::cpu_count() {
        Ok(count) => println!("cpus:     {count}"),
        Err(err) => eprintln!("cpus:     error: {err}"),
    }

    match ffi::load_average() {
        Ok([one, five, fifteen]) => println!("load:     {one:.2} {five:.2} {fifteen:.2}"),
        Err(err) => eprintln!("load:     error: {err}"),
    }

    ExitCode::SUCCESS
}
