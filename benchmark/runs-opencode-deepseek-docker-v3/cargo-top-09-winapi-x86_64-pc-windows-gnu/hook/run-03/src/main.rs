#[cfg(windows)]
fn main() {
    use windows::Win32::System::SystemInformation::GetTickCount;

    let uptime_ms = unsafe { GetTickCount() };
    println!("Windows uptime: {uptime_ms} ms");
}

#[cfg(not(windows))]
fn main() {
    eprintln!("This binary targets x86_64-pc-windows-gnu; run it on Windows.");
}
