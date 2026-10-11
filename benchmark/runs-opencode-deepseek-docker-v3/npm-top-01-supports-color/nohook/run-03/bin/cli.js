#!/usr/bin/env node
import process from "node:process";
import { createColors } from "../src/index.js";

const color = createColors(process.stdout);
const { support } = color;

const message = process.argv.slice(2).filter((arg) => !arg.startsWith("--")).join(" ");

function describeLevel(level) {
  switch (level) {
    case 0:
      return "none";
    case 1:
      return "basic (16 colors)";
    case 2:
      return "256 colors";
    case 3:
      return "truecolor (16m)";
    default:
      return "unknown";
  }
}

process.stdout.write(
  `${color.green("colorful")} ${color.dim(`v0.1.0`)}\n` +
    `${color.cyan("color support:")} ${describeLevel(support.level)}\n`,
);

if (message) {
  process.stdout.write(
    `${color.bold(color.yellow("message:"))} ${color.magenta(message)}\n`,
  );
}
