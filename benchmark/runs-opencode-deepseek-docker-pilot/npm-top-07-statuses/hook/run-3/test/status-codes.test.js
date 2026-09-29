import test from "node:test";
import assert from "node:assert/strict";
import { STATUS_CODES, getReasonPhrase, isKnownStatus } from "../src/status-codes.js";

test("looks up standard reason phrases", () => {
  assert.equal(getReasonPhrase(200), "OK");
  assert.equal(getReasonPhrase(404), "Not Found");
  assert.equal(getReasonPhrase(500), "Internal Server Error");
});

test("falls back for unknown codes", () => {
  assert.equal(getReasonPhrase(999), "Unknown Status Code");
});

test("isKnownStatus distinguishes known codes", () => {
  assert.equal(isKnownStatus(301), true);
  assert.equal(isKnownStatus(999), false);
});

test("all codes are three-digit numbers", () => {
  for (const code of Object.keys(STATUS_CODES)) {
    assert.match(code, /^\d{3}$/);
  }
});
