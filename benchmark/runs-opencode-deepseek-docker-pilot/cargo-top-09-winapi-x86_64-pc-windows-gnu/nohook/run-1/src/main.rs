use std::ptr;

use windows_sys::Win32::Foundation::HWND;
use windows_sys::Win32::UI::WindowsAndMessaging::{
    GetForegroundWindow, MessageBoxW, MB_ICONINFORMATION,
};

fn main() {
    let foreground: HWND = unsafe { GetForegroundWindow() };

    if foreground.is_null() {
        println!("no foreground window");
    } else {
        println!("foreground window handle: {foreground:?}");
    }

    if std::env::args().any(|arg| arg == "--show-message") {
        show_message("Hello from x86_64-pc-windows-gnu");
    }
}

fn show_message(text: &str) {
    let caption: Vec<u16> = "windows-sys bindings\0".encode_utf16().collect();
    let text: Vec<u16> = text.encode_utf16().chain(std::iter::once(0)).collect();

    unsafe {
        MessageBoxW(
            ptr::null_mut(),
            text.as_ptr(),
            caption.as_ptr(),
            MB_ICONINFORMATION,
        );
    }
}
