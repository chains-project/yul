use windows::{
    core::Result,
    Win32::Foundation::{CloseHandle, HANDLE},
    Win32::System::Diagnostics::Debug::GetLastError,
    Win32::System::Diagnostics::ToolHelp::{CreateToolhelp32Snapshot, TH32CS_SNAPPROCESS, PROCESSENTRY32},
    Win32::System::Threading::{OpenProcess, PROCESS_QUERY_INFORMATION, PROCESS_VM_READ},
};

fn main() -> Result<()> {
    println!("hook v0.1.0");
    println!("Cross-compiled for x86_64-pc-windows-gnu");

    // Example: Create a snapshot of running processes
    unsafe {
        let snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)?;
        println!("Process snapshot created (handle: {:?})", snapshot);
        CloseHandle(snapshot)?;
    }

    println!("Last error code: {}", unsafe { GetLastError() });

    Ok(())
}