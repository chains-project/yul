#[cfg(not(windows))]
compile_error!(
    "`win-tool` is Windows-only; build it with a Windows target such as \
     `x86_64-pc-windows-msvc`."
);

use windows::Win32::System::LibraryLoader::GetModuleHandleW;
use windows::Win32::System::Threading::GetCurrentProcessId;
use windows::Win32::UI::WindowsAndMessaging::{MB_ICONINFORMATION, MB_OK, MessageBoxW};
use windows::core::Result;

fn main() -> Result<()> {
    unsafe {
        let module = GetModuleHandleW(None)?;
        let pid = GetCurrentProcessId();
        println!("process id: {pid}");
        println!("module handle: {module:?}");

        let text = windows::core::w!("Direct bindings to the Windows API are working.");
        let caption = windows::core::w!("win-tool");
        MessageBoxW(None, text, caption, MB_OK | MB_ICONINFORMATION);
    }

    Ok(())
}
