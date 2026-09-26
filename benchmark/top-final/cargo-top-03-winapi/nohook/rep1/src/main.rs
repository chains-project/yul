#[cfg(windows)]
fn main() {
    use std::ffi::OsStr;
    use std::os::windows::ffi::OsStrExt;
    use std::ptr;

    use winapi::um::winuser::{MessageBoxW, MB_OK};

    fn to_wide(s: &str) -> Vec<u16> {
        OsStr::new(s).encode_wide().chain(Some(0)).collect()
    }

    let title = to_wide("windows_tool");
    let message = to_wide("Hello from a direct Windows API binding.");

    unsafe {
        MessageBoxW(ptr::null_mut(), message.as_ptr(), title.as_ptr(), MB_OK);
    }
}

#[cfg(not(windows))]
fn main() {
    compile_error!("windows_tool only builds on Windows targets");
}
