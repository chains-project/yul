const fs = require("fs");
const path = require("path");

const srcDir = path.join(__dirname, "..", "src");
const outDir = path.join(__dirname, "..", "dist");

fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(outDir, { recursive: true });

for (const file of fs.readdirSync(srcDir)) {
  fs.copyFileSync(path.join(srcDir, file), path.join(outDir, file));
}

fs.writeFileSync(
  path.join(outDir, "build-info.json"),
  JSON.stringify({ builtAt: new Date().toISOString() }, null, 2)
);

console.log(`Built ${fs.readdirSync(outDir).length} file(s) into dist/`);
