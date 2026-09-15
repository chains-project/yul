#[cfg(not(windows))]
compile_error!("winapi_tool binds directly to the Win32 API and only builds for Windows targets.");

#[cfg(windows)]
use std::ptr;
#[cfg(windows)]
use winapi::um::errhandlingapi::GetLastError;
#[cfg(windows)]
use winapi::um::winuser::{MessageBoxW, MB_ICONINFORMATION, MB_OK};

/// Encodes a Rust `&str` as a null-terminated UTF-16 buffer for wide Win32 APIs.
#[cfg(windows)]
fn to_wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(std::iter::once(0)).collect()
}

#[cfg(not(windows))]
fn main() {}

#[cfg(windows)]
fn main() {
    let title = to_wide("winapi_tool");
    let message = to_wide("Direct Windows API binding via winapi crate.");

    let result = unsafe {
        MessageBoxW(
            ptr::null_mut(),
            message.as_ptr(),
            title.as_ptr(),
            MB_OK | MB_ICONINFORMATION,
        )
    };

    if result == 0 {
        let error_code = unsafe { GetLastError() };
        eprintln!("MessageBoxW failed with error code: {error_code}");
        std::process::exit(1);
    }
}
