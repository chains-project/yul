use windows::core::w;
use windows::Win32::Foundation::{CloseHandle, HANDLE};
use windows::Win32::System::Diagnostics::ToolHelp::{
    CreateToolhelp32Snapshot, Process32First, Process32Next, PROCESSENTRY32, TH32CS_SNAPPROCESS,
};
use windows::Win32::System::Threading::{
    OpenProcess, PROCESS_QUERY_INFORMATION, PROCESS_VM_READ,
};

fn main() {
    println!("Hook tool - Windows API test");

    // Take a snapshot of all processes
    unsafe {
        let snapshot = match CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0) {
            Ok(h) => h,
            Err(e) => {
                eprintln!("Failed to create snapshot: {}", e);
                return;
            }
        };

        let mut entry: PROCESSENTRY32 = Default::default();
        entry.dwSize = std::mem::size_of::<PROCESSENTRY32>() as u32;

        let mut first = true;
        loop {
            let proc_entry = if first {
                first = false;
                Process32First(snapshot, &mut entry)
            } else {
                Process32Next(snapshot, &mut entry)
            };

            if proc_entry.is_ok() {
                let pid = entry.th32ProcessID;
                let name = String::from_utf16_lossless(
                    &entry.szExeFile
                        .iter()
                        .take_while(|&&c| c != 0)
                        .copied()
                        .collect::<Vec<_>>(),
                );
                println!("PID: {:>6} | {}", pid, name);
            } else {
                break;
            }
        }

        CloseHandle(snapshot).ok();
    }
}