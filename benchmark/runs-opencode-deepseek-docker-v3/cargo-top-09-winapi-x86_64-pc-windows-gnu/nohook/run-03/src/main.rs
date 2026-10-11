#[cfg(windows)]
mod app {
    use windows::core::PCWSTR;
    use windows::Win32::System::LibraryLoader::GetModuleHandleW;
    use windows::Win32::System::Threading::GetCurrentProcessId;
    use windows::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_ICONINFORMATION, MB_OK};

    fn wide(s: &str) -> Vec<u16> {
        s.encode_utf16().chain(std::iter::once(0)).collect()
    }

    pub fn run() {
        unsafe {
            let module = GetModuleHandleW(PCWSTR::null()).expect("GetModuleHandleW failed");
            let pid = GetCurrentProcessId();
            let text = wide(&format!(
                "Hello from Windows PID {pid} (module base {:#x})",
                module.0 as usize
            ));
            let caption = wide("winapi-cross");
            let _ = MessageBoxW(
                None,
                PCWSTR(text.as_ptr()),
                PCWSTR(caption.as_ptr()),
                MB_OK | MB_ICONINFORMATION,
            );
        }
    }
}

fn main() {
    #[cfg(windows)]
    app::run();

    #[cfg(not(windows))]
    println!("This binary targets x86_64-pc-windows-gnu.");
}
