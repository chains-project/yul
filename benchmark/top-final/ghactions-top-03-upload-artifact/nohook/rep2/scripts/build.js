const fs = require("fs");
const path = require("path");

const distDir = path.join(__dirname, "..", "dist");
fs.rmSync(distDir, { recursive: true, force: true });
fs.mkdirSync(distDir);
fs.copyFileSync(
  path.join(__dirname, "..", "src", "index.js"),
  path.join(distDir, "index.js")
);

console.log(`Build output written to ${distDir}`);
