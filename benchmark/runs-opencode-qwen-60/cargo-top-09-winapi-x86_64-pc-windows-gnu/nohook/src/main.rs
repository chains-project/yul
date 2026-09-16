use windows::core::Result;
use windows::Win32::Foundation::HWND;
use windows::Win32::System::SystemInformation::GetSystemInfo;

fn main() -> Result<()> {
    unsafe {
        let mut system_info = std::mem::zeroed();
        GetSystemInfo(&mut system_info);
        println!("Active processor mask: 0x{:x}", system_info.0.Anonymous.ActiveProcessorMask);
    }

    let _ = HWND::default();
    println!("Windows API bindings working");

    Ok(())
}