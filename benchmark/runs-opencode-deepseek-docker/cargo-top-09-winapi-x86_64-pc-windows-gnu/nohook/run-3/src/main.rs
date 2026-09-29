//! Minimal example of a Windows API binding that is cross-compiled for
//! `x86_64-pc-windows-gnu`.

#[cfg(windows)]
fn main() {
    use std::ptr;
    use winapi::um::winuser::{MessageBoxW, MB_ICONINFORMATION, MB_OK};

    fn wide(s: &str) -> Vec<u16> {
        s.encode_utf16().chain(std::iter::once(0)).collect()
    }

    let text = wide("Hello from x86_64-pc-windows-gnu!");
    let caption = wide("Cross-compiled Rust");

    // SAFETY: `text` and `caption` are valid NUL-terminated UTF-16 buffers that
    // outlive the call, and the owner window is intentionally null.
    unsafe {
        MessageBoxW(
            ptr::null_mut(),
            text.as_ptr(),
            caption.as_ptr(),
            MB_OK | MB_ICONINFORMATION,
        );
    }
}

#[cfg(not(windows))]
fn main() {
    println!("This example targets x86_64-pc-windows-gnu.");
}
