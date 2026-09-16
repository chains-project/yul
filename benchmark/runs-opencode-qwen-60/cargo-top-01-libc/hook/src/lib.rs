use std::ffi::CStr;

/// Example FFI function demonstrating use of C types and libc calls
pub fn get_hostname() -> String {
    let mut buf = [0i8; 256];
    unsafe {
        let ret = libc::gethostname(buf.as_mut_ptr(), buf.len());
        if ret == 0 {
            CStr::from_ptr(buf.as_ptr())
                .to_string_lossy()
                .into_owned()
        } else {
            String::from("error")
        }
    }
}