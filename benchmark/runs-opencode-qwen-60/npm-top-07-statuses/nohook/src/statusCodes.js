/**
 * HTTP Status Codes Lookup Table
 * Maps standard HTTP status codes to their reason phrases.
 */
const STATUS_CODES = {
  // 1xx: Informational
  100: 'Continue',
  101: 'Switching Protocols',
  102: 'Processing',
  103: 'Early Hints',

  // 2xx: Success
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

  // 3xx: Redirection
  300: 'Multiple Choices',
  301: 'Moved Permanently',
  302: 'Found',
  303: 'See Other',
  304: 'Not Modified',
  305: 'Use Proxy',
  307: 'Temporary Redirect',
  308: 'Permanent Redirect',

  // 4xx: Client Error
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
  413: 'Payload Too Large',
  414: 'URI Too Long',
  415: 'Unsupported Media Type',
  416: 'Range Not Satisfiable',
  417: 'Expectation Failed',
  418: "I'm a Teapot",
  421: 'Misdirected Request',
  422: 'Unprocessable Entity',
  423: 'Locked',
  424: 'Failed Dependency',
  425: 'Too Early',
  426: 'Upgrade Required',
  428: 'Precondition Required',
  429: 'Too Many Requests',
  431: 'Request Header Fields Too Large',
  451: 'Unavailable For Legal Reasons',

  // 5xx: Server Error
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
  511: 'Network Authentication Required'
};

/**
 * Get the reason phrase for a given status code.
 * @param {number} status - The HTTP status code.
 * @returns {string} The reason phrase, or 'Unknown' if not found.
 */
function getStatusPhrase(status) {
  if (typeof status !== 'number' || status < 100 || status > 599) {
    return 'Unknown';
  }
  return STATUS_CODES[status] || 'Unknown';
}

/**
 * Get all status codes as an array of objects.
 * @returns {Array<{code: number, phrase: string}>}
 */
function getAllStatuses() {
  return Object.entries(STATUS_CODES).map(([code, phrase]) => ({
    code: Number(code),
    phrase
  }));
}

/**
 * Get status codes filtered by category.
 * @param {'1xx'|'2xx'|'3xx'|'4xx'|'5xx'} category
 * @returns {Array<{code: number, phrase: string}>}
 */
function getStatusesByCategory(category) {
  const prefix = category.replace('xx', '');
  return getAllStatuses().filter(({ code }) => String(code).startsWith(prefix));
}

module.exports = {
  STATUS_CODES,
  getStatusPhrase,
  getAllStatuses,
  getStatusesByCategory
};