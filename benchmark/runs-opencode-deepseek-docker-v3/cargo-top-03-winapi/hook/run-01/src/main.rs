#[cfg(windows)]
mod app {
    use windows::Win32::UI::WindowsAndMessaging::{MB_ICONINFORMATION, MB_OK, MessageBoxW};
    use windows::core::{Result, w};

    pub fn run() -> Result<()> {
        unsafe {
            MessageBoxW(
                None,
                w!("Direct bindings to the Windows API are working."),
                w!("windows-tool"),
                MB_OK | MB_ICONINFORMATION,
            );
        }
        Ok(())
    }
}

#[cfg(windows)]
fn main() {
    if let Err(err) = app::run() {
        eprintln!("error: {err}");
        std::process::exit(1);
    }
}

#[cfg(not(windows))]
fn main() {
    compile_error!("windows-tool only builds on Windows.");
}
