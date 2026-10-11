#[cfg(not(windows))]
compile_error!("win-tool only supports Windows targets");

use windows::Win32::System::SystemInformation::{GetSystemInfo, SYSTEM_INFO};
use windows::Win32::UI::WindowsAndMessaging::{MB_ICONINFORMATION, MB_OK, MessageBoxW};
use windows::core::w;

fn main() {
    let info = system_info();

    let message = format!(
        "Processors: {}\nPage size: {} bytes",
        info.dwNumberOfProcessors, info.dwPageSize
    );

    unsafe {
        MessageBoxW(
            None,
            w!("Hello from the Windows API!"),
            w!("win-tool"),
            MB_OK | MB_ICONINFORMATION,
        );
    }

    println!("{message}");
}

fn system_info() -> SYSTEM_INFO {
    let mut info = SYSTEM_INFO::default();
    unsafe { GetSystemInfo(&mut info) };
    info
}
