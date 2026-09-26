#[cfg(not(windows))]
compile_error!("this tool only builds on Windows");

use std::ptr;
use winapi::um::winuser::{MessageBoxW, MB_OK};

fn to_wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(std::iter::once(0)).collect()
}

fn main() {
    let title = to_wide("windows_tool");
    let message = to_wide("Hello from the Windows API!");

    unsafe {
        MessageBoxW(ptr::null_mut(), message.as_ptr(), title.as_ptr(), MB_OK);
    }
}
