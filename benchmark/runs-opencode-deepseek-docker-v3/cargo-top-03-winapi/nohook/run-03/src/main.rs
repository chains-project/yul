#![cfg_attr(not(windows), allow(unused))]

#[cfg(not(windows))]
compile_error!(
    "win-tool is a Windows-only tool. Build it with a Windows target such as \
     x86_64-pc-windows-msvc."
);

#[cfg(not(windows))]
fn main() {}

#[cfg(windows)]
fn main() {
    use windows::Win32::System::Threading::GetCurrentProcessId;
    use windows::Win32::UI::WindowsAndMessaging::{MB_OK, MessageBoxW};
    use windows::core::w;

    let pid = unsafe { GetCurrentProcessId() };
    println!("win-tool running in process {pid}");

    unsafe {
        MessageBoxW(
            None,
            w!("Windows API bindings are wired up."),
            w!("win-tool"),
            MB_OK,
        );
    }
}
