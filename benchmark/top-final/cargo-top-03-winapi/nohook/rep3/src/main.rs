#[cfg(not(windows))]
compile_error!("this tool only builds on Windows");

use std::ffi::OsStr;
use std::iter::once;
use std::os::windows::ffi::OsStrExt;

use winapi::um::winuser::{MessageBoxW, MB_ICONINFORMATION, MB_OK};

fn to_wide(s: &str) -> Vec<u16> {
    OsStr::new(s).encode_wide().chain(once(0)).collect()
}

fn main() {
    let title = to_wide("winapi-tool");
    let message = to_wide("Hello from a direct Windows API binding!");

    unsafe {
        MessageBoxW(
            std::ptr::null_mut(),
            message.as_ptr(),
            title.as_ptr(),
            MB_OK | MB_ICONINFORMATION,
        );
    }
}
