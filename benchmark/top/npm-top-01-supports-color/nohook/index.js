import supportsColor from "supports-color";

const GREEN = "[32m";
const RESET = "[0m";

export function printMessage(message) {
  if (supportsColor.stdout) {
    console.log(`${GREEN}${message}${RESET}`);
  } else {
    console.log(message);
  }
}
