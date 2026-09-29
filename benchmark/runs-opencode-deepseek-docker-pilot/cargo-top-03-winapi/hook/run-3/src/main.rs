#[cfg(not(windows))]
compile_error!("win-tool is Windows-only and cannot be built for this target.");

#[cfg(windows)]
mod app;

#[cfg(windows)]
fn main() {
    app::run();
}
