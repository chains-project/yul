package main

import (
	"fmt"
	"log"
	"net/http"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "hello over %s\n", r.Proto)
	})

	mux.Handle("/ws", websocket.Handler(func(ws *websocket.Conn) {
		if _, err := ws.Write([]byte("connected\n")); err != nil {
			log.Printf("websocket write: %v", err)
		}
	}))

	h2s := &http2.Server{}
	handler := h2c.NewHandler(mux, h2s)

	log.Println("listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", handler))
}
