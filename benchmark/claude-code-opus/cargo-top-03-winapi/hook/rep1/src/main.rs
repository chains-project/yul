#[cfg(not(windows))]
compile_error!("wintool only supports Windows targets (e.g. x86_64-pc-windows-msvc).");

use windows::Win32::System::SystemInformation::{GetSystemInfo, SYSTEM_INFO};
use windows::Win32::System::Threading::GetCurrentProcessId;
use windows::Win32::UI::WindowsAndMessaging::{MB_ICONINFORMATION, MB_OK, MessageBoxW};
use windows::core::{HSTRING, w};

fn main() {
    let pid = unsafe { GetCurrentProcessId() };

    let mut info = SYSTEM_INFO::default();
    unsafe { GetSystemInfo(&mut info) };

    let text = HSTRING::from(format!(
        "PID: {pid}\nLogical processors: {}\nPage size: {} bytes",
        info.dwNumberOfProcessors, info.dwPageSize
    ));
    println!("{text}");

    unsafe { MessageBoxW(None, &text, w!("wintool"), MB_OK | MB_ICONINFORMATION) };
}
