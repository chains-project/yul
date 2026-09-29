// Local dogfood re-export: lets anyone opening this repo with `opencode`
// pick up the yul plugin without publishing/installing anything. Points at
// the package source directly (opencode-yul/), which is also what gets
// published to npm as "opencode-yul" for other projects to add to their
// opencode.json `plugin` array — see opencode-yul/src/index.ts for the
// actual implementation.
export { Yul } from "../../opencode-yul/src/index.js"
