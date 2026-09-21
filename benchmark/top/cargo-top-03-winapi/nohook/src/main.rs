#[cfg(not(windows))]
compile_error!("winapi-tool only builds for Windows targets");

#[cfg(windows)]
fn main() {
    use std::ffi::OsStr;
    use std::os::windows::ffi::OsStrExt;
    use std::ptr::null_mut;
    use winapi::um::winuser::{MessageBoxW, MB_OK};

    let text: Vec<u16> = OsStr::new("Hello from winapi!\0").encode_wide().collect();
    let caption: Vec<u16> = OsStr::new("winapi-tool\0").encode_wide().collect();

    unsafe {
        MessageBoxW(null_mut(), text.as_ptr(), caption.as_ptr(), MB_OK);
    }
}
