import { test } from "node:test";
import assert from "node:assert/strict";
import { STATUS_CODES, getReasonPhrase, isKnownStatus } from "../src/status-codes.js";

test("maps well-known status codes to their reason phrases", () => {
  assert.equal(STATUS_CODES[200], "OK");
  assert.equal(STATUS_CODES[404], "Not Found");
  assert.equal(STATUS_CODES[500], "Internal Server Error");
});

test("getReasonPhrase returns the phrase for known codes", () => {
  assert.equal(getReasonPhrase(201), "Created");
  assert.equal(getReasonPhrase(503), "Service Unavailable");
});

test("getReasonPhrase falls back for unknown codes", () => {
  assert.equal(getReasonPhrase(999), "Unknown Status");
  assert.equal(getReasonPhrase(999, "Custom"), "Custom");
});

test("isKnownStatus distinguishes known from unknown codes", () => {
  assert.equal(isKnownStatus(418), true);
  assert.equal(isKnownStatus(299), false);
});

test("lookup table is immutable", () => {
  assert.ok(Object.isFrozen(STATUS_CODES));
});
