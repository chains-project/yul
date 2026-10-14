mod config;

use config::CONFIG;

fn main() {
    // First access triggers initialization.
    println!("{} starting", CONFIG.app_name);
    println!("worker threads: {}", CONFIG.worker_threads);
    println!("debug: {}", CONFIG.debug);
    println!("started at (unix): {}", CONFIG.started_unix_secs);
    println!("uptime: {:?}", CONFIG.started_at.elapsed());
}
