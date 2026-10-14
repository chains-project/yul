use windows_sys::Win32::Foundation::HWND;
use windows_sys::Win32::UI::WindowsAndMessaging::{MB_ICONINFORMATION, MB_OK, MESSAGEBOX_RESULT, MESSAGEBOX_STYLE};
use windows_sys::core::PCWSTR;

// Resolved through the windows_x86_64_gnu import library.
windows_targets::link!("kernel32.dll" "system" fn GetCurrentProcessId() -> u32);
windows_targets::link!("user32.dll" "system" fn MessageBoxW(hwnd: HWND, text: PCWSTR, caption: PCWSTR, utype: MESSAGEBOX_STYLE) -> MESSAGEBOX_RESULT);

fn wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(std::iter::once(0)).collect()
}

fn main() {
    let pid = unsafe { GetCurrentProcessId() };
    println!("Hello from Windows, PID {pid}");

    let text = wide(&format!("Running as process {pid}"));
    let caption = wide("win-app");
    unsafe {
        MessageBoxW(
            std::ptr::null_mut(),
            text.as_ptr(),
            caption.as_ptr(),
            MB_OK | MB_ICONINFORMATION,
        );
    }
}
