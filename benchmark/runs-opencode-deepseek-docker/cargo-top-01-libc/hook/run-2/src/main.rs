use sys_tool as sys;

fn main() {
    println!("== sys-tool ==");

    match sys::process_name() {
        Ok(name) => println!("process name : {name}"),
        Err(e) => eprintln!("process name : error: {e}"),
    }
    println!("pid          : {}", sys::pid());
    println!("uid          : {}", sys::uid());

    match sys::hostname() {
        Ok(host) => println!("hostname     : {host}"),
        Err(e) => eprintln!("hostname     : error: {e}"),
    }
    match sys::page_size() {
        Ok(size) => println!("page size    : {size} bytes"),
        Err(e) => eprintln!("page size    : error: {e}"),
    }
    match sys::cpu_count() {
        Ok(n) => println!("online CPUs  : {n}"),
        Err(e) => eprintln!("online CPUs  : error: {e}"),
    }

    match std::env::args().nth(1) {
        Some(arg) => match sys::parse_i64(&arg) {
            Ok(value) => println!("parsed i64   : {value}"),
            Err(e) => eprintln!("parsed i64   : error: {e}"),
        },
        None => println!("(pass an integer argument to exercise native parsing)"),
    }

    println!("fnv1a(b\"sys-tool\") = 0x{:016x}", sys::fnv1a(b"sys-tool"));
}
