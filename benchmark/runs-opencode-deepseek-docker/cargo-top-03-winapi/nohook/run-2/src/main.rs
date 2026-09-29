#[cfg(not(windows))]
compile_error!("windows-tool only builds for Windows.");

#[cfg(windows)]
fn main() {
    use windows::Win32::System::Threading::GetCurrentProcessId;

    // SAFETY: GetCurrentProcessId has no preconditions and cannot fail.
    let pid = unsafe { GetCurrentProcessId() };
    println!("current process id: {pid}");
}
