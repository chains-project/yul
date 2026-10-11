use libc::{c_long, off_t, pid_t, size_t};

#[repr(C)]
pub struct ExampleStats {
    pub count: size_t,
    pub total: off_t,
}

unsafe extern "C" {
    fn example_sum(values: *const c_long, len: size_t) -> c_long;
    fn example_pid() -> pid_t;
    fn example_collect(values: *const c_long, len: size_t, out: *mut ExampleStats);
}

pub fn sum(values: &[i64]) -> i64 {
    let len = values.len() as size_t;
    let ptr = values.as_ptr().cast::<c_long>();
    unsafe { example_sum(ptr, len) as i64 }
}

pub fn pid() -> pid_t {
    unsafe { example_pid() }
}

pub fn collect(values: &[i64]) -> ExampleStats {
    let mut stats = ExampleStats { count: 0, total: 0 };
    let len = values.len() as size_t;
    let ptr = values.as_ptr().cast::<c_long>();
    unsafe { example_collect(ptr, len, &mut stats) };
    stats
}
