mod ffi;

fn main() -> std::io::Result<()> {
    println!("pid       = {}", ffi::current_pid());
    println!("hostname  = {}", ffi::hostname()?);

    let data = b"hello from Rust";
    println!("checksum  = {}", ffi::sum_bytes(data));

    let mut buf = [0u8; 8];
    let written = ffi::fill(&mut buf, b'x');
    println!("filled    = {} bytes -> {:?}", written, buf);

    Ok(())
}
