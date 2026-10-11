#[cfg(windows)]
fn main() {
    use std::ffi::OsStr;
    use std::iter;
    use std::os::windows::ffi::OsStrExt;
    use std::ptr;

    use winapi::um::winuser::{MessageBoxW, MB_ICONINFORMATION, MB_OK};

    fn wide(s: &str) -> Vec<u16> {
        OsStr::new(s).encode_wide().chain(iter::once(0)).collect()
    }

    let text = wide("Built for x86_64-pc-windows-gnu with Windows API import libraries.");
    let caption = wide("windows-gnu-cross");

    unsafe {
        MessageBoxW(
            ptr::null_mut(),
            text.as_ptr(),
            caption.as_ptr(),
            MB_OK | MB_ICONINFORMATION,
        );
    }
}

#[cfg(not(windows))]
fn main() {
    println!("This crate targets x86_64-pc-windows-gnu.");
    println!("Build it with: cargo build --target x86_64-pc-windows-gnu");
}
