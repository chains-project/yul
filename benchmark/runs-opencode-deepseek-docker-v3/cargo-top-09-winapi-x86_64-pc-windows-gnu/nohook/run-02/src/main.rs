#[cfg(windows)]
fn main() {
    use windows_sys::Win32::System::SystemInformation::{GetSystemInfo, SYSTEM_INFO};
    use windows_sys::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_ICONINFORMATION, MB_OK};

    let mut info = unsafe { std::mem::zeroed::<SYSTEM_INFO>() };
    unsafe { GetSystemInfo(&mut info) };
    let arch = unsafe { info.Anonymous.Anonymous.wProcessorArchitecture };

    println!("Windows API SYSTEM_INFO (linked against kernel32 import library):");
    println!("  processor architecture : {}", arch);
    println!("  logical processors     : {}", info.dwNumberOfProcessors);
    println!("  page size              : {} bytes", info.dwPageSize);
    println!("  allocation granularity : {} bytes", info.dwAllocationGranularity);

    if std::env::args().any(|a| a == "--msgbox") {
        let text: Vec<u16> = "Hello from Rust on x86_64-pc-windows-gnu\0".encode_utf16().collect();
        let caption: Vec<u16> = "win-cross\0".encode_utf16().collect();
        unsafe {
            MessageBoxW(
                std::ptr::null_mut(),
                text.as_ptr(),
                caption.as_ptr(),
                MB_OK | MB_ICONINFORMATION,
            );
        }
    }
}

#[cfg(not(windows))]
fn main() {
    eprintln!("This binary is built for the x86_64-pc-windows-gnu target.");
}
