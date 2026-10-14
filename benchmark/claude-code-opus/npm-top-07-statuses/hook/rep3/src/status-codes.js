/**
 * HTTP status codes and their standard reason phrases.
 *
 * Phrases follow the IANA HTTP Status Code Registry
 * (https://www.iana.org/assignments/http-status-codes), which reflects
 * RFC 9110 naming — e.g. 413 "Content Too Large" and 422 "Unprocessable
 * Content" rather than the older "Payload Too Large" / "Unprocessable Entity".
 * 418 is included for compatibility despite being reserved/unused.
 */
export const STATUS_CODES = Object.freeze({
  // 1xx Informational
  100: 'Continue',
  101: 'Switching Protocols',
  102: 'Processing',
  103: 'Early Hints',

  // 2xx Success
  200: 'OK',
  201: 'Created',
  202: 'Accepted',
  203: 'Non-Authoritative Information',
  204: 'No Content',
  205: 'Reset Content',
  206: 'Partial Content',
  207: 'Multi-Status',
  208: 'Already Reported',
  226: 'IM Used',

  // 3xx Redirection
  300: 'Multiple Choices',
  301: 'Moved Permanently',
  302: 'Found',
  303: 'See Other',
  304: 'Not Modified',
  305: 'Use Proxy',
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
  418: "I'm a Teapot",
  421: 'Misdirected Request',
  422: 'Unprocessable Content',
  423: 'Locked',
  424: 'Failed Dependency',
  425: 'Too Early',
  426: 'Upgrade Required',
  428: 'Precondition Required',
  429: 'Too Many Requests',
  431: 'Request Header Fields Too Large',
  451: 'Unavailable For Legal Reasons',

  // 5xx Server Error
  500: 'Internal Server Error',
  501: 'Not Implemented',
  502: 'Bad Gateway',
  503: 'Service Unavailable',
  504: 'Gateway Timeout',
  505: 'HTTP Version Not Supported',
  506: 'Variant Also Negotiates',
  507: 'Insufficient Storage',
  508: 'Loop Detected',
  510: 'Not Extended',
  511: 'Network Authentication Required',
});

/** Returns the reason phrase for `code`, or undefined if it isn't registered. */
export function reasonPhrase(code) {
  return Object.hasOwn(STATUS_CODES, code) ? STATUS_CODES[code] : undefined;
}

/** Returns the status class of `code`, e.g. 'success' for 204. */
export function statusClass(code) {
  if (!Number.isInteger(code) || code < 100 || code > 599) return undefined;
  return ['informational', 'success', 'redirection', 'client_error', 'server_error'][
    Math.floor(code / 100) - 1
  ];
}
