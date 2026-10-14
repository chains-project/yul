/**
 * HTTP status codes and their standard reason phrases.
 *
 * Source: IANA HTTP Status Code Registry, using the phrases defined in
 * RFC 9110 (HTTP Semantics) and the extension RFCs it references.
 * Note that RFC 9110 renamed 413 ("Payload Too Large") and 422
 * ("Unprocessable Entity"); the current names are used here. 418 is
 * reserved/unused in the registry and is intentionally omitted.
 */
export const STATUS_CODES = Object.freeze({
  // 1xx Informational
  100: 'Continue',
  101: 'Switching Protocols',
  102: 'Processing', // RFC 2518
  103: 'Early Hints', // RFC 8297

  // 2xx Success
  200: 'OK',
  201: 'Created',
  202: 'Accepted',
  203: 'Non-Authoritative Information',
  204: 'No Content',
  205: 'Reset Content',
  206: 'Partial Content',
  207: 'Multi-Status', // RFC 4918
  208: 'Already Reported', // RFC 5842
  226: 'IM Used', // RFC 3229

  // 3xx Redirection
  300: 'Multiple Choices',
  301: 'Moved Permanently',
  302: 'Found',
  303: 'See Other',
  304: 'Not Modified',
  305: 'Use Proxy', // deprecated
  307: 'Temporary Redirect',
  308: 'Permanent Redirect',

  // 4xx Client Error
  400: 'Bad Request',
  401: 'Unauthorized',
  402: 'Payment Required',
  403: 'Forbidden',
  404: 'Not Found',
  405: 'Method Not Allowed',
  406: 'Not Acceptable',
  407: 'Proxy Authentication Required',
  408: 'Request Timeout',
  409: 'Conflict',
  410: 'Gone',
  411: 'Length Required',
  412: 'Precondition Failed',
  413: 'Content Too Large',
  414: 'URI Too Long',
  415: 'Unsupported Media Type',
  416: 'Range Not Satisfiable',
  417: 'Expectation Failed',
  421: 'Misdirected Request',
  422: 'Unprocessable Content',
  423: 'Locked', // RFC 4918
  424: 'Failed Dependency', // RFC 4918
  425: 'Too Early', // RFC 8470
  426: 'Upgrade Required',
  428: 'Precondition Required', // RFC 6585
  429: 'Too Many Requests', // RFC 6585
  431: 'Request Header Fields Too Large', // RFC 6585
  451: 'Unavailable For Legal Reasons', // RFC 7725

  // 5xx Server Error
  500: 'Internal Server Error',
  501: 'Not Implemented',
  502: 'Bad Gateway',
  503: 'Service Unavailable',
  504: 'Gateway Timeout',
  505: 'HTTP Version Not Supported',
  506: 'Variant Also Negotiates', // RFC 2295
  507: 'Insufficient Storage', // RFC 4918
  508: 'Loop Detected', // RFC 5842
  510: 'Not Extended', // RFC 2774, obsoleted
  511: 'Network Authentication Required', // RFC 6585
});

/**
 * Returns the reason phrase for a status code, or undefined if unknown.
 * @param {number|string} code
 * @returns {string|undefined}
 */
export function getReasonPhrase(code) {
  return Object.hasOwn(STATUS_CODES, code) ? STATUS_CODES[code] : undefined;
}

/**
 * Returns the class of a status code ("informational", "success",
 * "redirection", "client_error", "server_error"), or undefined if the
 * code is outside 100–599.
 * @param {number} code
 * @returns {string|undefined}
 */
export function getStatusClass(code) {
  const n = Number(code);
  if (!Number.isInteger(n) || n < 100 || n > 599) return undefined;
  return ['informational', 'success', 'redirection', 'client_error', 'server_error'][
    Math.floor(n / 100) - 1
  ];
}
