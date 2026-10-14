use windows_sys::Win32::Foundation::HWND;
use windows_sys::Win32::UI::WindowsAndMessaging::{MB_OK, MESSAGEBOX_RESULT, MESSAGEBOX_STYLE};
use windows_sys::core::PCWSTR;
use windows_sys::w;

windows_targets::link!("kernel32.dll" "system" fn GetCurrentProcessId() -> u32);
windows_targets::link!("user32.dll" "system" fn MessageBoxW(hwnd: HWND, text: PCWSTR, caption: PCWSTR, utype: MESSAGEBOX_STYLE) -> MESSAGEBOX_RESULT);

fn main() {
    let pid = unsafe { GetCurrentProcessId() };
    println!("Hello from Windows, pid {pid}");

    unsafe {
        MessageBoxW(
            std::ptr::null_mut(),
            w!("Hello from Rust!"),
            w!("win_app"),
            MB_OK,
        );
    }
}
