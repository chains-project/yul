package mapfluent

import (
	"strconv"
	"strings"
)

type segment struct {
	key     string
	index   int
	isIndex bool
	append  bool
}

func parsePath(path string) []segment {
	path = strings.TrimSpace(path)
	path = strings.TrimPrefix(path, "$")
	path = strings.TrimPrefix(path, ".")
	if path == "" {
		return nil
	}

	var (
		segs []segment
		key  strings.Builder
	)

	flush := func() {
		if key.Len() > 0 {
			segs = append(segs, segment{key: key.String()})
			key.Reset()
		}
	}

	for i := 0; i < len(path); i++ {
		switch c := path[i]; c {
		case '\\':
			if i+1 < len(path) {
				i++
				key.WriteByte(path[i])
			} else {
				key.WriteByte(c)
			}
		case '.':
			flush()
		case '[':
			flush()
			end := strings.IndexByte(path[i:], ']')
			if end < 0 {
				key.WriteByte(c)
				continue
			}
			inner := path[i+1 : i+end]
			i += end
			switch {
			case inner == "" || inner == "-":
				segs = append(segs, segment{isIndex: true, append: true})
			default:
				if n, err := strconv.Atoi(inner); err == nil {
					segs = append(segs, segment{isIndex: true, index: n})
				} else {
					segs = append(segs, segment{key: strings.Trim(inner, `"'`)})
				}
			}
		default:
			key.WriteByte(c)
		}
	}
	flush()

	return segs
}
