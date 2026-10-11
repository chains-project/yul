#[cfg(not(windows))]
fn main() {
    compile_error!("win-tool is a Windows-only tool and cannot be built on this platform");
}

#[cfg(windows)]
use std::ffi::OsString;
#[cfg(windows)]
use std::os::windows::ffi::OsStringExt;

#[cfg(windows)]
use windows_sys::Win32::System::Threading::GetCurrentProcessId;
#[cfg(windows)]
use windows_sys::Win32::System::WindowsProgramming::GetComputerNameW;

#[cfg(windows)]
fn computer_name() -> String {
    let mut buf = [0u16; 256];
    let mut len = buf.len() as u32;
    let ok = unsafe { GetComputerNameW(buf.as_mut_ptr(), &mut len) };
    assert_ne!(ok, 0, "GetComputerNameW failed");
    OsString::from_wide(&buf[..len as usize])
        .to_string_lossy()
        .into_owned()
}

#[cfg(windows)]
fn main() {
    let pid = unsafe { GetCurrentProcessId() };
    println!("computer: {} (pid {})", computer_name(), pid);
}
