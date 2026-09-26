#[cfg(windows)]
use winapi::um::processthreadsapi::GetCurrentProcessId;
#[cfg(windows)]
use winapi::um::winuser::{MessageBoxW, MB_OK};

#[cfg(windows)]
fn main() {
    let pid = unsafe { GetCurrentProcessId() };
    println!("current process id: {}", pid);

    let text: Vec<u16> = "Hello from winapi!\0".encode_utf16().collect();
    let caption: Vec<u16> = "winapi-demo\0".encode_utf16().collect();
    unsafe {
        MessageBoxW(
            std::ptr::null_mut(),
            text.as_ptr(),
            caption.as_ptr(),
            MB_OK,
        );
    }
}

#[cfg(not(windows))]
fn main() {
    println!("this binary targets windows; build with --target x86_64-pc-windows-gnu");
}
