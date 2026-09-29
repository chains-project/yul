use windows_sys::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_ICONINFORMATION, MB_OK};

fn main() {
    let caption: Vec<u16> = "win-hello\0".encode_utf16().collect();
    let text: Vec<u16> = "Hello from x86_64-pc-windows-gnu!\0".encode_utf16().collect();

    unsafe {
        MessageBoxW(
            std::ptr::null_mut(),
            text.as_ptr(),
            caption.as_ptr(),
            MB_OK | MB_ICONINFORMATION,
        );
    }
}
