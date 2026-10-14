use windows_sys::Win32::System::Threading::GetCurrentProcessId;
use windows_sys::Win32::UI::WindowsAndMessaging::{MB_OK, MessageBoxA};

fn main() {
    let pid = unsafe { GetCurrentProcessId() };
    println!("Hello from Windows! PID = {pid}");

    let text = format!("Running as process {pid}\0");
    unsafe {
        MessageBoxA(
            std::ptr::null_mut(),
            text.as_ptr(),
            c"win_app".as_ptr().cast(),
            MB_OK,
        );
    }
}
