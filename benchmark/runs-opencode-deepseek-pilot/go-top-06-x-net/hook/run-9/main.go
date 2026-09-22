package main

import (
	"io"
	"log"
	"net/http"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func main() {
	mux := http.NewServeMux()
	mux.Handle("/ws", websocket.Handler(echo))
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("hello over " + r.Proto))
	})

	srv := &http.Server{
		Addr:              ":8080",
		Handler:           h2c.NewHandler(mux, &http2.Server{}),
		ReadHeaderTimeout: 5 * time.Second,
	}

	log.Println("listening on", srv.Addr)
	log.Fatal(srv.ListenAndServe())
}

func echo(ws *websocket.Conn) {
	if _, err := io.Copy(ws, ws); err != nil {
		log.Println("websocket:", err)
	}
}
