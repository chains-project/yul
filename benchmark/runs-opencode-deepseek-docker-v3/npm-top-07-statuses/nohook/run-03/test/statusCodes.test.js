import test from "node:test";
import assert from "node:assert/strict";
import { STATUS_CODES, isValidStatus, reasonPhrase } from "../src/statusCodes.js";

test("lookup table contains common status codes", () => {
  assert.equal(STATUS_CODES[200], "OK");
  assert.equal(STATUS_CODES[404], "Not Found");
  assert.equal(STATUS_CODES[500], "Internal Server Error");
});

test("reasonPhrase returns the standard phrase", () => {
  assert.equal(reasonPhrase(201), "Created");
  assert.equal(reasonPhrase(418), "I'm a Teapot");
});

test("reasonPhrase falls back for unknown codes", () => {
  assert.equal(reasonPhrase(999), "Unknown");
});

test("isValidStatus accepts in-range integer codes only", () => {
  assert.equal(isValidStatus(100), true);
  assert.equal(isValidStatus(599), true);
  assert.equal(isValidStatus(99), false);
  assert.equal(isValidStatus(600), false);
  assert.equal(isValidStatus(20.5), false);
  assert.equal(isValidStatus("200"), false);
});
