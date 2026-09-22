package main

import (
	"io"
	"log"
	"net/http"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func main() {
	mux := http.NewServeMux()

	mux.Handle("/ws", websocket.Handler(func(ws *websocket.Conn) {
		io.Copy(ws, ws)
	}))

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("ok"))
	})

	h2s := &http2.Server{}
	handler := h2c.NewHandler(mux, h2s)

	log.Println("listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", handler))
}
