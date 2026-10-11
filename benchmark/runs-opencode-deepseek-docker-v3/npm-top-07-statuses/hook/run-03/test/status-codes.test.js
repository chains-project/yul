import assert from "node:assert/strict";
import test from "node:test";
import { reasonPhrase, statusCodes } from "../src/status-codes.js";

test("looks up standard reason phrases", () => {
  assert.equal(reasonPhrase(200), "OK");
  assert.equal(reasonPhrase(404), "Not Found");
  assert.equal(reasonPhrase(500), "Internal Server Error");
});

test("falls back for unknown codes", () => {
  assert.equal(reasonPhrase(599), "Unknown");
  assert.equal(reasonPhrase(599, "Custom"), "Custom");
});

test("table covers common codes", () => {
  for (const code of [200, 201, 204, 301, 400, 401, 403, 404, 500, 503]) {
    assert.ok(typeof statusCodes[code] === "string");
  }
});
