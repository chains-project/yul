mod ffi;

fn main() {
    let text = c"hello from C";
    let len = ffi::c_strlen(text);
    println!("pid={} strlen={}", ffi::pid(), len);
}
