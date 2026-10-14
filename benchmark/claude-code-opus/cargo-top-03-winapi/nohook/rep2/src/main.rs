#[cfg(not(windows))]
compile_error!("wintool only supports Windows targets (e.g. --target x86_64-pc-windows-msvc)");

use windows::Win32::System::SystemInformation::{GetSystemInfo, GetTickCount64, SYSTEM_INFO};
use windows::Win32::System::Threading::GetCurrentProcessId;

fn main() -> windows::core::Result<()> {
    // SAFETY: these Win32 calls have no preconditions; GetSystemInfo writes into a
    // properly sized, stack-allocated SYSTEM_INFO.
    let (pid, uptime_ms, info) = unsafe {
        let mut info = SYSTEM_INFO::default();
        GetSystemInfo(&mut info);
        (GetCurrentProcessId(), GetTickCount64(), info)
    };

    println!("pid:        {pid}");
    println!("processors: {}", info.dwNumberOfProcessors);
    println!("page size:  {} bytes", info.dwPageSize);
    println!("uptime:     {}s", uptime_ms / 1000);
    Ok(())
}
