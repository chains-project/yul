#[cfg(not(windows))]
compile_error!("winapi-tool only builds for Windows targets, e.g. `cargo build --target x86_64-pc-windows-msvc`");

#[cfg(windows)]
use windows::Win32::System::Console::{GetConsoleWindow, SetConsoleTitleW};
#[cfg(windows)]
use windows::core::PCWSTR;

#[cfg(windows)]
fn main() {
    let title: Vec<u16> = "winapi-tool\0".encode_utf16().collect();
    unsafe {
        let _ = SetConsoleTitleW(PCWSTR(title.as_ptr()));
        let hwnd = GetConsoleWindow();
        println!("console window handle: {:?}", hwnd);
    }
}
