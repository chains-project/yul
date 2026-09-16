use winapi::um::winuser::{MessageBoxW, MB_ICONINFORMATION, MB_OK};
use winapi::shared::windef::HWND;

fn main() {
    let text = "Hello from Rust using direct WinAPI!\0".encode_utf16().collect::<Vec<_>>();
    let caption = "WinAPI Tool\0".encode_utf16().collect::<Vec<_>>();
    
    unsafe {
        MessageBoxW(
            std::ptr::null_mut() as HWND,
            text.as_ptr(),
            caption.as_ptr(),
            MB_OK | MB_ICONINFORMATION,
        );
    }
}