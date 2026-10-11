import process from "node:process";

const { env, argv, platform } = process;

const CI_ENV_VARS = [
  "CI",
  "CONTINUOUS_INTEGRATION",
  "BUILD_NUMBER",
  "RUN_ID",
  "GITHUB_ACTIONS",
  "GITLAB_CI",
  "CIRCLECI",
  "TRAVIS",
  "APPVEYOR",
  "BUILDKITE",
  "DRONE",
  "JENKINS_URL",
  "TEAMCITY_VERSION",
  "TF_BUILD",
  "CODEBUILD_BUILD_ID",
];

function translateLevel(level) {
  const clamped = Math.max(0, Math.min(3, level));
  return Object.freeze({
    level: clamped,
    supported: clamped > 0,
    hasBasic: clamped >= 1,
    has256: clamped >= 2,
    has16m: clamped >= 3,
  });
}

function forceColorLevel() {
  if (!("FORCE_COLOR" in env)) {
    return undefined;
  }

  const value = env.FORCE_COLOR;
  if (value === "true" || value === "") {
    return 1;
  }
  if (value === "false") {
    return 0;
  }
  const parsed = Number.parseInt(value, 10);
  return Number.isNaN(parsed) ? 1 : parsed;
}

function sniffColorFlags(args) {
  if (
    args.includes("--no-color") ||
    args.includes("--no-colors") ||
    args.includes("--color=false") ||
    args.includes("--color=never")
  ) {
    return 0;
  }
  if (
    args.includes("--color") ||
    args.includes("--colors") ||
    args.includes("--color=true") ||
    args.includes("--color=always")
  ) {
    return 1;
  }
  if (args.includes("--color=256")) {
    return 2;
  }
  if (args.includes("--color=16m") || args.includes("--color=full")) {
    return 3;
  }
  return undefined;
}

function isCI() {
  return CI_ENV_VARS.some((name) => name in env && env[name]);
}

function getColorSupport(stream = process.stdout, options = {}) {
  const { sniffFlags = true } = options;

  const forced = forceColorLevel();
  if (forced !== undefined) {
    return translateLevel(forced);
  }

  if (sniffFlags) {
    const flagged = sniffColorFlags(argv.slice(2));
    if (flagged !== undefined) {
      return translateLevel(flagged);
    }
  }

  if ("NO_COLOR" in env || "NODE_DISABLE_COLORS" in env) {
    return translateLevel(0);
  }

  if (env.TERM === "dumb") {
    return translateLevel(0);
  }

  if (platform === "win32") {
    if (env.WT_SESSION || env.TERM_PROGRAM) {
      return translateLevel(3);
    }
    if (env.ANSICON || env.ConEmuANSI === "ON" || isCI()) {
      return translateLevel(1);
    }
    if (env.COLORTERM) {
      return translateLevel(3);
    }
  }

  if (!stream?.isTTY) {
    return translateLevel(isCI() ? 1 : 0);
  }

  if (env.COLORTERM === "truecolor" || env.COLORTERM === "24bit") {
    return translateLevel(3);
  }
  if (/256color/i.test(env.TERM ?? "")) {
    return translateLevel(2);
  }
  if (/truecolor|24bit/i.test(env.TERM ?? "") || env.TERM_PROGRAM === "iTerm.app") {
    return translateLevel(3);
  }
  if (env.TERM) {
    return translateLevel(1);
  }

  return translateLevel(1);
}

function supportsColor(stream = process.stdout, options = {}) {
  return getColorSupport(stream, options).supported;
}

export { getColorSupport, supportsColor, translateLevel, forceColorLevel, sniffColorFlags };
