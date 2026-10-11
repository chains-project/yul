package mapfluent

func (m Map) Set(path string, value any) Map {
	segs := parsePath(path)
	if len(segs) == 0 || segs[0].isIndex || m == nil {
		return m
	}
	setInto(map[string]any(m), segs, value)
	return m
}

func (m Map) SetDefault(path string, value any) Map {
	if !m.Has(path) {
		m.Set(path, value)
	}
	return m
}

func (m Map) EnsureMap(path string) Map {
	if existing, ok := toMapAnyOK(m.Get(path)); ok {
		return existing
	}
	segs := parsePath(path)
	if len(segs) == 0 || segs[len(segs)-1].isIndex || segs[0].isIndex || m == nil {
		return nil
	}
	m.Set(path, map[string]any{})
	if created, ok := toMapAnyOK(m.Get(path)); ok {
		return created
	}
	return nil
}

func (m Map) Delete(path string) Map {
	segs := parsePath(path)
	if len(segs) == 0 || segs[0].isIndex || m == nil {
		return m
	}
	deleteInto(map[string]any(m), segs)
	return m
}

func (m Map) Merge(other Map) Map {
	if m == nil {
		return other
	}
	mergeInto(map[string]any(m), map[string]any(other))
	return m
}

func (m Map) Clone() Map {
	return Map(cloneValue(map[string]any(m)).(map[string]any))
}

func setInto(node map[string]any, segs []segment, value any) {
	seg := segs[0]
	if len(segs) == 1 {
		node[seg.key] = value
		return
	}
	next := segs[1]
	if next.isIndex {
		arr, ok := toSliceAnyOK(node[seg.key])
		if !ok {
			arr = []any{}
		}
		arr = setSlice(arr, segs[1:], value)
		node[seg.key] = arr
		return
	}
	child, ok := toMapAnyOK(node[seg.key])
	if !ok {
		child = Map{}
	}
	setInto(map[string]any(child), segs[1:], value)
	node[seg.key] = map[string]any(child)
}

func setSlice(arr []any, segs []segment, value any) []any {
	seg := segs[0]
	idx := seg.index
	if seg.append {
		idx = len(arr)
	}
	if idx < 0 {
		return arr
	}
	for len(arr) <= idx {
		arr = append(arr, nil)
	}
	if len(segs) == 1 {
		arr[idx] = value
		return arr
	}
	next := segs[1]
	if next.isIndex {
		child, ok := toSliceAnyOK(arr[idx])
		if !ok {
			child = []any{}
		}
		arr[idx] = setSlice(child, segs[1:], value)
		return arr
	}
	childMap, ok := toMapAnyOK(arr[idx])
	if !ok {
		childMap = Map{}
	}
	setInto(map[string]any(childMap), segs[1:], value)
	arr[idx] = map[string]any(childMap)
	return arr
}

func deleteInto(node map[string]any, segs []segment) {
	seg := segs[0]
	if len(segs) == 1 {
		delete(node, seg.key)
		return
	}
	child, ok := node[seg.key]
	if !ok {
		return
	}
	next := segs[1]
	if next.isIndex {
		arr, ok := toSliceAnyOK(child)
		if !ok {
			return
		}
		if out, ok := deleteSlice(arr, segs[1:]); ok {
			node[seg.key] = out
		}
		return
	}
	childMap, ok := toMapAnyOK(child)
	if !ok {
		return
	}
	deleteInto(map[string]any(childMap), segs[1:])
	node[seg.key] = map[string]any(childMap)
}

func deleteSlice(arr []any, segs []segment) ([]any, bool) {
	seg := segs[0]
	idx := seg.index
	if idx < 0 || idx >= len(arr) {
		return arr, false
	}
	if len(segs) == 1 {
		out := make([]any, 0, len(arr)-1)
		out = append(out, arr[:idx]...)
		out = append(out, arr[idx+1:]...)
		return out, true
	}
	next := segs[1]
	if next.isIndex {
		child, ok := toSliceAnyOK(arr[idx])
		if !ok {
			return arr, false
		}
		out, ok := deleteSlice(child, segs[1:])
		if !ok {
			return arr, false
		}
		arr[idx] = out
		return arr, true
	}
	childMap, ok := toMapAnyOK(arr[idx])
	if !ok {
		return arr, false
	}
	deleteInto(map[string]any(childMap), segs[1:])
	arr[idx] = map[string]any(childMap)
	return arr, true
}

func mergeInto(dst, src map[string]any) {
	for k, v := range src {
		if sv, ok := toMapAnyOK(v); ok {
			if dv, ok := toMapAnyOK(dst[k]); ok {
				mergeInto(map[string]any(dv), map[string]any(sv))
				dst[k] = map[string]any(dv)
				continue
			}
		}
		dst[k] = v
	}
}

func cloneValue(v any) any {
	switch x := v.(type) {
	case Map:
		out := make(map[string]any, len(x))
		for k, vv := range x {
			out[k] = cloneValue(vv)
		}
		return Map(out)
	case map[string]any:
		out := make(map[string]any, len(x))
		for k, vv := range x {
			out[k] = cloneValue(vv)
		}
		return out
	case []any:
		out := make([]any, len(x))
		for i, vv := range x {
			out[i] = cloneValue(vv)
		}
		return out
	default:
		return v
	}
}
