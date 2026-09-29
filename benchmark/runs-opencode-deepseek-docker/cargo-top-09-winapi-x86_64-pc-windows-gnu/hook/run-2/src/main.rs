use core::ptr::null_mut;
use core::mem::zeroed;
use windows_sys::Win32::System::SystemInformation::{GetSystemInfo, SYSTEM_INFO};
use windows_sys::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_ICONINFORMATION, MB_OK};

fn main() {
    unsafe {
        let mut info: SYSTEM_INFO = zeroed();
        GetSystemInfo(&mut info);

        let message = format!("Logical processors: {}", info.dwNumberOfProcessors);
        println!("{message}");

        let text: Vec<u16> = message.encode_utf16().chain(core::iter::once(0)).collect();
        let caption: Vec<u16> = "winapi-gnu-cross"
            .encode_utf16()
            .chain(core::iter::once(0))
            .collect();

        MessageBoxW(
            null_mut(),
            text.as_ptr(),
            caption.as_ptr(),
            MB_OK | MB_ICONINFORMATION,
        );
    }
}
