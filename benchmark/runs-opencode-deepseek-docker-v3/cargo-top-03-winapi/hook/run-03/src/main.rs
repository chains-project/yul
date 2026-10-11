#[cfg(not(windows))]
compile_error!("windows-tool only builds on Windows.");

#[cfg(windows)]
fn main() {
    let mut info = windows::Win32::System::SystemInformation::SYSTEM_INFO::default();
    unsafe {
        windows::Win32::System::SystemInformation::GetSystemInfo(&mut info);
    }
    println!(
        "windows-tool: {} logical processors, page size {}",
        info.dwNumberOfProcessors, info.dwPageSize
    );
}
