use std::ffi::CString;
use std::ptr;

use winapi::um::winuser::{MessageBoxA, MB_OK};

fn main() {
    let title = CString::new("winapi-demo").unwrap();
    let message = CString::new("Hello from x86_64-pc-windows-gnu!").unwrap();

    unsafe {
        MessageBoxA(ptr::null_mut(), message.as_ptr(), title.as_ptr(), MB_OK);
    }
}
