#[cfg(not(windows))]
compile_error!("winhook-tool only builds on Windows (it links directly against the Win32 API)");

use winapi::um::handleapi::CloseHandle;
use winapi::um::processthreadsapi::{GetCurrentProcessId, OpenProcess};
use winapi::um::winnt::PROCESS_QUERY_INFORMATION;
use winapi::um::winuser::{MessageBoxW, MB_OK};

fn to_wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(std::iter::once(0)).collect()
}

fn main() {
    let pid = unsafe { GetCurrentProcessId() };

    // Round-trip through OpenProcess/CloseHandle to prove the process handle APIs link.
    let handle = unsafe { OpenProcess(PROCESS_QUERY_INFORMATION, 0, pid) };
    if !handle.is_null() {
        unsafe { CloseHandle(handle) };
    }

    let text = to_wide(&format!("Running as PID {pid}"));
    let caption = to_wide("winhook-tool");

    unsafe {
        MessageBoxW(std::ptr::null_mut(), text.as_ptr(), caption.as_ptr(), MB_OK);
    }
}
