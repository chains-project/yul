use std::ffi::OsStr;
use std::iter::once;
use std::os::windows::ffi::OsStrExt;
use std::ptr::null_mut;

use winapi::um::winuser::{MessageBoxW, MB_OK};

fn to_wide(s: &str) -> Vec<u16> {
    OsStr::new(s).encode_wide().chain(once(0)).collect()
}

fn main() {
    let title = to_wide("winapi_demo");
    let message = to_wide("Hello from a cross-compiled x86_64-pc-windows-gnu binary!");

    unsafe {
        MessageBoxW(null_mut(), message.as_ptr(), title.as_ptr(), MB_OK);
    }
}
