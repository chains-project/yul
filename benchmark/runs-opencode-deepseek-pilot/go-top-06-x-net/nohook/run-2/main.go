package main

import (
	"log"
	"net/http"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func main() {
	mux := http.NewServeMux()

	mux.Handle("/ws", websocket.Handler(func(ws *websocket.Conn) {
		if _, err := ws.Write([]byte("hello from websocket")); err != nil {
			log.Printf("websocket write: %v", err)
		}
	}))

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		proto := r.Proto
		if r.ProtoMajor == 2 {
			proto = "HTTP/2"
		}
		_, _ = w.Write([]byte("protocol: " + proto + "\n"))
	})

	h2s := &http2.Server{}
	handler := h2c.NewHandler(mux, h2s)

	log.Println("listening on :8080")
	if err := http.ListenAndServe(":8080", handler); err != nil {
		log.Fatal(err)
	}
}
