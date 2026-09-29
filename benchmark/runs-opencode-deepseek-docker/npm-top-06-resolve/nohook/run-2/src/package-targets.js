function resolveConditionalTarget(target, conditions) {
  if (target === null) return null;
  if (typeof target === 'string') return target;
  if (Array.isArray(target)) {
    for (const item of target) {
      const resolved = resolveConditionalTarget(item, conditions);
      if (resolved != null) return resolved;
    }
    return null;
  }
  if (typeof target === 'object') {
    for (const key of Object.keys(target)) {
      if (key === 'default' || conditions.includes(key)) {
        const resolved = resolveConditionalTarget(target[key], conditions);
        if (resolved != null) return resolved;
      }
    }
    return null;
  }
  return null;
}

function isSubpathMap(map, kind) {
  const keys = Object.keys(map);
  if (keys.length === 0) return false;
  return keys.every((key) =>
    kind === 'imports' ? key.startsWith('#') : key === '.' || key.startsWith('./'),
  );
}

function matchPattern(map, request, conditions, kind) {
  for (const key of Object.keys(map)) {
    const star = key.indexOf('*');
    if (star === -1) continue;
    const prefix = key.slice(0, star);
    const suffix = key.slice(star + 1);
    if (
      request.length >= prefix.length + suffix.length &&
      request.startsWith(prefix) &&
      request.endsWith(suffix)
    ) {
      const matched = request.slice(prefix.length, request.length - suffix.length);
      const target = resolveConditionalTarget(map[key], conditions);
      if (typeof target === 'string') {
        return target.split('*').join(matched);
      }
    }
  }
  return null;
}

export function resolvePackageMap(map, request, conditions, kind) {
  if (map == null) return null;

  if (typeof map !== 'object' || Array.isArray(map)) {
    if (kind === 'exports' && request === '.') {
      return resolveConditionalTarget(map, conditions);
    }
    return null;
  }

  if (!isSubpathMap(map, kind)) {
    if (kind === 'exports' && request === '.') {
      return resolveConditionalTarget(map, conditions);
    }
    return null;
  }

  if (Object.prototype.hasOwnProperty.call(map, request)) {
    return resolveConditionalTarget(map[request], conditions);
  }

  return matchPattern(map, request, conditions, kind);
}
