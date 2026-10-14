#[cfg(not(windows))]
compile_error!("wintool only supports Windows targets (e.g. x86_64-pc-windows-msvc).");

use windows::Win32::System::SystemInformation::{
    ComputerNamePhysicalDnsHostname, GetComputerNameExW,
};
use windows::Win32::System::Threading::GetCurrentProcessId;
use windows::core::{PWSTR, Result};

fn computer_name() -> Result<String> {
    let mut len = 0u32;
    // First call fails with ERROR_MORE_DATA and reports the required buffer size.
    let _ = unsafe { GetComputerNameExW(ComputerNamePhysicalDnsHostname, None, &mut len) };

    let mut buf = vec![0u16; len as usize];
    unsafe {
        GetComputerNameExW(
            ComputerNamePhysicalDnsHostname,
            Some(PWSTR(buf.as_mut_ptr())),
            &mut len,
        )?;
    }
    Ok(String::from_utf16_lossy(&buf[..len as usize]))
}

fn main() -> Result<()> {
    let pid = unsafe { GetCurrentProcessId() };
    println!("Host: {}", computer_name()?);
    println!("PID:  {pid}");
    Ok(())
}
