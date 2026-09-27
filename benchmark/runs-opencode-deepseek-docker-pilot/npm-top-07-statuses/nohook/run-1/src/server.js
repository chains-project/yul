'use strict';

const http = require('node:http');
const { STATUS_CODES, getReasonPhrase, isStatusCode } = require('./status-codes');

function sendJson(res, statusCode, payload) {
  const body = JSON.stringify(payload, null, 2);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body)
  });
  res.end(body);
}

function handleRequest(req, res) {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const segments = url.pathname.split('/').filter(Boolean);

  if (req.method !== 'GET') {
    sendJson(res, 405, { error: getReasonPhrase(405) });
    return;
  }

  if (segments.length === 0) {
    sendJson(res, 200, {
      name: 'http-status-server',
      endpoints: {
        'GET /status': 'List every known status code and reason phrase.',
        'GET /status/:code': 'Respond with the given status code and its reason phrase.'
      }
    });
    return;
  }

  if (segments[0] !== 'status') {
    sendJson(res, 404, { error: getReasonPhrase(404) });
    return;
  }

  if (segments.length === 1) {
    sendJson(res, 200, { statusCodes: STATUS_CODES });
    return;
  }

  const raw = segments[1];

  if (!/^\d{3}$/.test(raw) || !isStatusCode(raw)) {
    sendJson(res, 400, { error: getReasonPhrase(400), code: raw });
    return;
  }

  const code = Number(raw);
  sendJson(res, code, { code, reason: getReasonPhrase(code) });
}

function createServer() {
  return http.createServer(handleRequest);
}

module.exports = { createServer, handleRequest };
