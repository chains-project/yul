use windows_sys::Win32::Foundation::HWND;
use windows_sys::Win32::UI::WindowsAndMessaging::{MB_ICONINFORMATION, MB_OK, MessageBoxW};

fn wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(std::iter::once(0)).collect()
}

fn main() {
    let text = wide("Hello from Rust, cross-compiled for x86_64-pc-windows-gnu");
    let caption = wide("winbind");

    unsafe {
        MessageBoxW(
            std::ptr::null_mut::<core::ffi::c_void>() as HWND,
            text.as_ptr(),
            caption.as_ptr(),
            MB_OK | MB_ICONINFORMATION,
        );
    }
}
