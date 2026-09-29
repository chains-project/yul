//! A Windows-only command-line tool built directly on the Win32 API.
//!
//! The Windows API calls live behind `#[cfg(windows)]` so the project still
//! type-checks on other hosts, while a clear message is printed if it is ever
//! launched somewhere other than Windows.

#[cfg(windows)]
mod app {
    use windows_sys::Win32::System::SystemInformation::{GetSystemInfo, SYSTEM_INFO};
    use windows_sys::Win32::System::Threading::GetCurrentProcessId;

    pub fn run() {
        // Every Win32 FFI call is `unsafe`: the caller must uphold the API's
        // contract (valid pointers, correct types, expected initialization).
        let pid = unsafe { GetCurrentProcessId() };

        // SYSTEM_INFO is plain-old-data, so a zeroed value is a valid starting
        // point before the API fills it in.
        let mut info = unsafe { std::mem::zeroed::<SYSTEM_INFO>() };
        unsafe { GetSystemInfo(&mut info) };

        println!("process id:      {pid}");
        println!("processor count: {}", info.dwNumberOfProcessors);
        println!("page size:       {} bytes", info.dwPageSize);
    }
}

#[cfg(windows)]
fn main() {
    app::run();
}

#[cfg(not(windows))]
fn main() {
    eprintln!("wintool is a Windows-only tool.");
    std::process::exit(1);
}
