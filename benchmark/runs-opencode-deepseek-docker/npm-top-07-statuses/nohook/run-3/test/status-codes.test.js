import { test } from "node:test";
import assert from "node:assert/strict";
import {
  STATUS_CODES,
  getReasonPhrase,
  getStatusCode,
  isStatusCode,
} from "../src/status-codes.js";

test("maps well-known codes to their reason phrases", () => {
  assert.equal(getReasonPhrase(200), "OK");
  assert.equal(getReasonPhrase(301), "Moved Permanently");
  assert.equal(getReasonPhrase(404), "Not Found");
  assert.equal(getReasonPhrase(500), "Internal Server Error");
});

test("getReasonPhrase accepts numeric strings", () => {
  assert.equal(getReasonPhrase("418"), "I'm a Teapot");
});

test("getReasonPhrase returns undefined for unknown codes", () => {
  assert.equal(getReasonPhrase(999), undefined);
});

test("getStatusCode performs the reverse lookup", () => {
  assert.equal(getStatusCode("No Content"), 204);
  assert.equal(getStatusCode("Not a real phrase"), undefined);
});

test("isStatusCode validates known codes", () => {
  assert.equal(isStatusCode(200), true);
  assert.equal(isStatusCode("418"), true);
  assert.equal(isStatusCode(999), false);
  assert.equal(isStatusCode("nope"), false);
});

test("lookup table is frozen", () => {
  assert.equal(Object.isFrozen(STATUS_CODES), true);
});
