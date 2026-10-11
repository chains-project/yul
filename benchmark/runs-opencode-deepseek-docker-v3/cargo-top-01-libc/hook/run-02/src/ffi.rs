use libc::{c_char, c_int, c_long, dev_t, gid_t, ino_t, pid_t, uid_t};
use std::ffi::CStr;
use std::io;

#[repr(C)]
#[derive(Debug, Clone, Copy, Default)]
pub struct ProcInfo {
    pub pid: pid_t,
    pub uid: uid_t,
    pub gid: gid_t,
    pub page_size: c_long,
}

unsafe extern "C" {
    fn systool_proc_info_get(out: *mut ProcInfo) -> c_int;
    fn systool_page_size() -> c_long;
    fn systool_file_dev_ino(path: *const c_char, dev: *mut dev_t, ino: *mut ino_t) -> c_int;
}

pub fn proc_info() -> io::Result<ProcInfo> {
    let mut info = ProcInfo::default();
    let rc = unsafe { systool_proc_info_get(&mut info) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(info)
}

pub fn page_size() -> c_long {
    unsafe { systool_page_size() }
}

pub fn file_dev_ino(path: &CStr) -> io::Result<(dev_t, ino_t)> {
    let mut dev: dev_t = 0;
    let mut ino: ino_t = 0;
    let rc = unsafe { systool_file_dev_ino(path.as_ptr(), &mut dev, &mut ino) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok((dev, ino))
}
