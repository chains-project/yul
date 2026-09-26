const fs = require("fs");
const path = require("path");

const distDir = path.join(__dirname, "..", "dist");
fs.mkdirSync(distDir, { recursive: true });
fs.copyFileSync(
  path.join(__dirname, "..", "src", "index.js"),
  path.join(distDir, "index.js")
);

console.log("Build output written to dist/");
