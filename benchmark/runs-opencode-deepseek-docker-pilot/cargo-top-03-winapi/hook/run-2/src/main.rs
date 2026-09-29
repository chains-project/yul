// This tool talks to the Win32 API directly, so it only builds for Windows.
#[cfg(not(windows))]
compile_error!(
    "winapi-tool targets Windows only. Build with a Windows target, e.g. \
     `cargo build --target x86_64-pc-windows-msvc`."
);

#[cfg(not(windows))]
fn main() {}

#[cfg(windows)]
fn main() {
    use windows::core::{w, PCWSTR};
    use windows::Win32::System::Threading::GetCurrentThreadId;
    use windows::Win32::UI::WindowsAndMessaging::{
        MessageBoxW, MB_ICONINFORMATION, MB_OK, MESSAGEBOX_STYLE,
    };

    // SAFETY: no arguments, no preconditions.
    let thread_id = unsafe { GetCurrentThreadId() };

    let message = format!("winapi-tool is running on thread {thread_id}.");
    let message: Vec<u16> = message.encode_utf16().chain(std::iter::once(0)).collect();

    // SAFETY: `message` is a valid NUL-terminated UTF-16 string that outlives the call.
    unsafe {
        MessageBoxW(
            None,
            PCWSTR(message.as_ptr()),
            w!("winapi-tool"),
            MESSAGEBOX_STYLE(MB_OK.0 | MB_ICONINFORMATION.0),
        );
    }
}
