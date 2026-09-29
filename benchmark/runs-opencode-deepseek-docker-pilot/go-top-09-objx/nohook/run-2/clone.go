package dynmap

// cloneValue deep copies nested maps and []interface{} slices. Other
// values are returned as-is.
func cloneValue(v interface{}) interface{} {
	switch t := v.(type) {
	case map[string]interface{}:
		out := make(map[string]interface{}, len(t))
		for k, val := range t {
			out[k] = cloneValue(val)
		}
		return out
	case []interface{}:
		out := make([]interface{}, len(t))
		for i, val := range t {
			out[i] = cloneValue(val)
		}
		return out
	default:
		return v
	}
}
