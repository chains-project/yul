#[cfg(not(windows))]
compile_error!("wintool only supports Windows targets");

use windows_sys::Win32::System::Threading::GetCurrentProcessId;
use windows_sys::Win32::UI::WindowsAndMessaging::{MB_ICONINFORMATION, MB_OK, MessageBoxW};

/// Encodes a Rust string as a NUL-terminated UTF-16 buffer for `*W` Win32 APIs.
fn wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(std::iter::once(0)).collect()
}

fn main() {
    // SAFETY: GetCurrentProcessId has no preconditions.
    let pid = unsafe { GetCurrentProcessId() };

    let text = wide(&format!("Hello from wintool (PID {pid})"));
    let caption = wide("wintool");

    // SAFETY: both pointers reference live, NUL-terminated UTF-16 buffers
    // that outlive the call; a null HWND means "no owner window".
    unsafe {
        MessageBoxW(
            std::ptr::null_mut(),
            text.as_ptr(),
            caption.as_ptr(),
            MB_OK | MB_ICONINFORMATION,
        );
    }
}
