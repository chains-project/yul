#[cfg(windows)]
fn show_message() {
    use std::ffi::OsStr;
    use std::iter::once;
    use std::os::windows::ffi::OsStrExt;
    use std::ptr::null_mut;
    use winapi::um::winuser::{MessageBoxW, MB_OK};

    let title: Vec<u16> = OsStr::new("winapi_demo").encode_wide().chain(once(0)).collect();
    let text: Vec<u16> = OsStr::new("Hello from winapi!").encode_wide().chain(once(0)).collect();

    unsafe {
        MessageBoxW(null_mut(), text.as_ptr(), title.as_ptr(), MB_OK);
    }
}

#[cfg(not(windows))]
fn show_message() {
    println!("Hello from winapi_demo (build for x86_64-pc-windows-gnu to see the message box)");
}

fn main() {
    show_message();
}
