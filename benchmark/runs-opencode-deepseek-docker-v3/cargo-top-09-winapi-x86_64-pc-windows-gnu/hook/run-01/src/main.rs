#[cfg(windows)]
mod bindings {
    use windows_targets::link;

    link!("kernel32.dll" "system" fn GetCurrentProcessId() -> u32);
    link!("kernel32.dll" "system" fn GetTickCount() -> u32);
    link!("kernel32.dll" "system" fn GetLastError() -> u32);
    link!("kernel32.dll" "system" fn SetLastError(dwErrCode: u32));
}

fn main() {
    #[cfg(windows)]
    {
        unsafe {
            bindings::SetLastError(0);
            println!(
                "pid: {}, uptime: {} ms, last error: {}",
                bindings::GetCurrentProcessId(),
                bindings::GetTickCount(),
                bindings::GetLastError(),
            );
        }
    }

    #[cfg(not(windows))]
    {
        eprintln!("build this program for x86_64-pc-windows-gnu");
    }
}
