package main

import (
	"net/http/httptest"
	"strings"
	"testing"

	"golang.org/x/net/websocket"
)

func TestEcho(t *testing.T) {
	srv := httptest.NewServer(websocket.Handler(echo))
	defer srv.Close()

	url := "ws" + strings.TrimPrefix(srv.URL, "http")
	ws, err := websocket.Dial(url, "", srv.URL)
	if err != nil {
		t.Fatal(err)
	}
	defer ws.Close()

	if err := websocket.Message.Send(ws, "ping"); err != nil {
		t.Fatal(err)
	}
	var got string
	if err := websocket.Message.Receive(ws, &got); err != nil {
		t.Fatal(err)
	}
	if got != "ping" {
		t.Fatalf("got %q, want %q", got, "ping")
	}
}
