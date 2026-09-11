use std::ptr;
use winapi::um::libloaderapi::GetModuleHandleW;
use winapi::um::winuser::{MessageBoxW, MB_OK};

fn to_wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(std::iter::once(0)).collect()
}

fn main() {
    let title = to_wide("winapi_demo");
    let message = to_wide("Hello from x86_64-pc-windows-gnu!");

    unsafe {
        let _hinstance = GetModuleHandleW(ptr::null());
        MessageBoxW(ptr::null_mut(), message.as_ptr(), title.as_ptr(), MB_OK);
    }
}
