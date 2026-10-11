#[cfg(not(windows))]
compile_error!("win-tool only supports Windows targets (e.g. x86_64-pc-windows-msvc).");

#[cfg(windows)]
fn main() {
    use windows::Win32::System::Console::SetConsoleTitleW;
    use windows::Win32::System::Threading::{GetCurrentProcessId, GetCurrentThreadId};

    let pid = unsafe { GetCurrentProcessId() };
    let tid = unsafe { GetCurrentThreadId() };

    let title = format!("win-tool - pid {pid}, tid {tid}");
    let wide: Vec<u16> = title.encode_utf16().chain(std::iter::once(0)).collect();
    unsafe {
        let _ = SetConsoleTitleW(windows::core::PCWSTR(wide.as_ptr()));
    }

    println!("{title}");
}
