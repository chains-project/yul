package netapp_test

import (
	"crypto/tls"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/websocket"

	"netapp/internal/netapp"
)

func TestHealthOverHTTP1(t *testing.T) {
	srv := httptest.NewServer(netapp.New().Handler())
	defer srv.Close()

	resp, err := http.Get(srv.URL + "/healthz")
	if err != nil {
		t.Fatalf("get: %v", err)
	}
	defer resp.Body.Close()

	if resp.ProtoMajor != 1 {
		t.Fatalf("ProtoMajor = %d, want 1", resp.ProtoMajor)
	}
	assertHealthy(t, resp)
}

func TestHealthOverHTTP2(t *testing.T) {
	srv := httptest.NewUnstartedServer(netapp.New().Handler())
	srv.EnableHTTP2 = true
	srv.StartTLS()
	defer srv.Close()

	client := &http.Client{
		Transport: &http2.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
	}

	resp, err := client.Get(srv.URL + "/healthz")
	if err != nil {
		t.Fatalf("get: %v", err)
	}
	defer resp.Body.Close()

	if resp.ProtoMajor != 2 {
		t.Fatalf("ProtoMajor = %d, want 2", resp.ProtoMajor)
	}
	assertHealthy(t, resp)
}

func TestWebSocketEcho(t *testing.T) {
	srv := httptest.NewServer(netapp.New().Handler())
	defer srv.Close()

	wsURL := "ws" + strings.TrimPrefix(srv.URL, "http") + "/ws"
	conn, err := websocket.Dial(wsURL, "", "http://localhost/")
	if err != nil {
		t.Fatalf("dial: %v", err)
	}
	defer conn.Close()
	_ = conn.SetDeadline(time.Now().Add(5 * time.Second))

	const want = "hello over websocket"
	if _, err := io.WriteString(conn, want); err != nil {
		t.Fatalf("write: %v", err)
	}

	buf := make([]byte, len(want))
	if _, err := io.ReadFull(conn, buf); err != nil {
		t.Fatalf("read: %v", err)
	}
	if got := string(buf); got != want {
		t.Fatalf("echo = %q, want %q", got, want)
	}
}

func assertHealthy(t *testing.T, resp *http.Response) {
	t.Helper()
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status = %d, want 200", resp.StatusCode)
	}
	var body map[string]string
	if err := json.NewDecoder(resp.Body).Decode(&body); err != nil {
		t.Fatalf("decode: %v", err)
	}
	if body["status"] != "ok" {
		t.Fatalf("status field = %q, want ok", body["status"])
	}
}
