#!/usr/bin/env node
import { printMessage } from "../index.js";

const message = process.argv.slice(2).join(" ") || "Hello from color-cli!";

printMessage(message);
