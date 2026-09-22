package main

import (
	"fmt"
	"log"
	"net/http"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		proto := r.Proto
		fmt.Fprintf(w, "hello from %s\n", proto)
	})

	mux.Handle("/ws", websocket.Handler(func(ws *websocket.Conn) {
		defer ws.Close()
		buf := make([]byte, 1024)
		for {
			n, err := ws.Read(buf)
			if err != nil {
				return
			}
			if _, err := ws.Write(buf[:n]); err != nil {
				return
			}
		}
	}))

	h2s := &http2.Server{}
	srv := &http.Server{
		Addr:              ":8080",
		Handler:           h2c.NewHandler(mux, h2s),
		ReadHeaderTimeout: 5 * time.Second,
	}

	log.Printf("listening on %s (h2c)", srv.Addr)
	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatal(err)
	}
}
