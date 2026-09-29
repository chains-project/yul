//! Minimal Win32 application cross-compiled for `x86_64-pc-windows-gnu`.
//!
//! The `#[link(name = "...")]` attributes below are what make this crate
//! require the MinGW-w64 import libraries (`libuser32.a`, `libkernel32.a`, ...)
//! that live in the cross sysroot.

use std::ffi::c_void;
use std::iter::once;

type Hwnd = *mut c_void;

const MB_OK: u32 = 0x0000_0000;
const MB_ICONINFORMATION: u32 = 0x0000_0040;

#[link(name = "user32")]
unsafe extern "system" {
    fn MessageBoxW(hwnd: Hwnd, text: *const u16, caption: *const u16, u_type: u32) -> i32;
}

#[link(name = "kernel32")]
unsafe extern "system" {
    fn GetConsoleWindow() -> Hwnd;
}

fn wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(once(0)).collect()
}

fn main() {
    let text = wide("Hello from x86_64-pc-windows-gnu!");
    let caption = wide("windows-gnu-demo");
    let owner = unsafe { GetConsoleWindow() };

    unsafe {
        MessageBoxW(
            owner,
            text.as_ptr(),
            caption.as_ptr(),
            MB_OK | MB_ICONINFORMATION,
        );
    }
}
