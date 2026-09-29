import { test } from "node:test";
import assert from "node:assert/strict";
import { reasonPhrase, isStatusCode, statusCodes } from "../src/status-codes.js";

test("returns standard reason phrases", () => {
  assert.equal(reasonPhrase(200), "OK");
  assert.equal(reasonPhrase(404), "Not Found");
  assert.equal(reasonPhrase(500), "Internal Server Error");
  assert.equal(reasonPhrase(418), "I'm a Teapot");
});

test("throws on unknown status codes", () => {
  assert.throws(() => reasonPhrase(999), RangeError);
});

test("isStatusCode distinguishes known codes", () => {
  assert.equal(isStatusCode(204), true);
  assert.equal(isStatusCode(999), false);
});

test("exposes the full lookup table", () => {
  assert.ok(Object.keys(statusCodes).length > 50);
});
