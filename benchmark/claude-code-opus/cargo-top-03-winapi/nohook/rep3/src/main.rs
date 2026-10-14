#[cfg(not(windows))]
compile_error!("win-tool only supports Windows targets");

use windows_sys::Win32::System::Threading::GetCurrentProcessId;
use windows_sys::Win32::UI::WindowsAndMessaging::{MB_ICONINFORMATION, MB_OK, MessageBoxW};
use windows_sys::w;

fn main() {
    // SAFETY: GetCurrentProcessId has no preconditions.
    let pid = unsafe { GetCurrentProcessId() };
    println!("Running as process {pid}");

    // SAFETY: a null owner window is allowed, and `w!` produces
    // NUL-terminated UTF-16 string literals with 'static lifetime.
    unsafe {
        MessageBoxW(
            std::ptr::null_mut(),
            w!("Hello from the Windows API"),
            w!("win-tool"),
            MB_OK | MB_ICONINFORMATION,
        );
    }
}
