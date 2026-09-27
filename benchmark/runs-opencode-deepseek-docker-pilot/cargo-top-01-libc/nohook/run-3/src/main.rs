mod ffi;
mod sys;

use std::io;
use std::process::ExitCode;

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(err) => {
            eprintln!("systool: {err}");
            ExitCode::FAILURE
        }
    }
}

fn run() -> io::Result<()> {
    println!("pid          : {}", sys::pid());
    println!("uid          : {}", sys::uid());
    println!("page size    : {} bytes", sys::page_size()?);
    println!("architecture : {}", sys::machine()?);
    Ok(())
}
