use std::ptr::null_mut;

use windows_sys::Win32::System::Threading::GetCurrentProcessId;
use windows_sys::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_OK};

fn to_wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(std::iter::once(0)).collect()
}

pub fn run() {
    let pid = unsafe { GetCurrentProcessId() };
    let text = to_wide(&format!("Hello from direct Win32 bindings.\nProcess ID: {pid}"));
    let caption = to_wide("win-tool");

    unsafe {
        MessageBoxW(null_mut(), text.as_ptr(), caption.as_ptr(), MB_OK);
    }
}
