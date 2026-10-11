use windows::core::PCWSTR;
use windows::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_OK};

fn main() {
    let text: Vec<u16> = "Hello from Rust on Windows (GNU toolchain)\0".encode_utf16().collect();
    let caption: Vec<u16> = "winapp\0".encode_utf16().collect();

    unsafe {
        MessageBoxW(
            None,
            PCWSTR(text.as_ptr()),
            PCWSTR(caption.as_ptr()),
            MB_OK,
        );
    }
}
