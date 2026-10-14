#[cfg(not(windows))]
compile_error!("wintool only supports Windows targets (e.g. x86_64-pc-windows-msvc).");

use windows::Win32::System::SystemInformation::{ComputerNameDnsHostname, GetComputerNameExW};
use windows::Win32::System::Threading::GetCurrentProcessId;
use windows::core::PWSTR;

fn main() -> windows::core::Result<()> {
    let pid = unsafe { GetCurrentProcessId() };
    println!("pid:      {pid}");
    println!("hostname: {}", computer_name()?);
    Ok(())
}

/// Returns the DNS hostname of the local machine.
fn computer_name() -> windows::core::Result<String> {
    // First call with no buffer to learn the required size (including the NUL).
    let mut len = 0u32;
    let _ = unsafe { GetComputerNameExW(ComputerNameDnsHostname, None, &mut len) };

    let mut buf = vec![0u16; len as usize];
    unsafe {
        GetComputerNameExW(
            ComputerNameDnsHostname,
            Some(PWSTR(buf.as_mut_ptr())),
            &mut len,
        )?
    };

    // On success, `len` is the number of characters written, excluding the NUL.
    Ok(String::from_utf16_lossy(&buf[..len as usize]))
}
