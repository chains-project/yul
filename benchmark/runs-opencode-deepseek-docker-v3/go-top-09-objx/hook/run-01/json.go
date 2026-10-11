package mapfluent

import (
	"bytes"
	"encoding/json"
)

func Decode(data []byte) (Map, error) {
	out := New()
	if err := json.Unmarshal(data, &out); err != nil {
		return nil, err
	}
	if out == nil {
		out = New()
	}
	return out, nil
}

func DecodeString(s string) (Map, error) {
	return Decode([]byte(s))
}

func MustDecode(data []byte) Map {
	out, err := Decode(data)
	if err != nil {
		panic(err)
	}
	return out
}

func MustDecodeString(s string) Map {
	return MustDecode([]byte(s))
}

func (m Map) Encode() ([]byte, error) {
	return json.Marshal(map[string]any(m))
}

func (m Map) EncodeIndent(prefix, indent string) ([]byte, error) {
	return json.MarshalIndent(map[string]any(m), prefix, indent)
}

func (m Map) MustEncode() []byte {
	out, err := m.Encode()
	if err != nil {
		panic(err)
	}
	return out
}

func (m Map) WriteTo(w *bytes.Buffer) error {
	out, err := m.Encode()
	if err != nil {
		return err
	}
	_, err = w.Write(out)
	return err
}
