#[cfg(not(windows))]
compile_error!(
    "this tool only supports Windows; build with e.g. \
     `cargo build --target x86_64-pc-windows-msvc`"
);

use windows::core::w;
use windows::Win32::System::Threading::GetCurrentProcessId;
use windows::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_ICONINFORMATION, MB_OK};

fn main() {
    // SAFETY: GetCurrentProcessId takes no arguments and cannot fail.
    let pid = unsafe { GetCurrentProcessId() };
    println!("current process id: {pid}");

    // SAFETY: the PCWSTR literals outlive the call, and `None` is a valid
    // parent window handle for a message box.
    let _ = unsafe {
        MessageBoxW(
            None,
            w!("Direct Win32 bindings are working."),
            w!("windows-tool"),
            MB_OK | MB_ICONINFORMATION,
        )
    };
}
