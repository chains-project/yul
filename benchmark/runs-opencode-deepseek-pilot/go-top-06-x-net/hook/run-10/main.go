package main

import (
	"io"
	"log"
	"net/http"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func echo(ws *websocket.Conn) {
	if _, err := io.Copy(ws, ws); err != nil {
		log.Printf("websocket copy: %v", err)
	}
}

func main() {
	mux := http.NewServeMux()
	mux.Handle("/ws", websocket.Handler(echo))
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain")
		_, _ = w.Write([]byte("ok\n"))
	})

	h2s := &http2.Server{}
	srv := &http.Server{
		Addr:    ":8080",
		Handler: h2c.NewHandler(mux, h2s),
	}

	log.Printf("listening on %s", srv.Addr)
	log.Fatal(srv.ListenAndServe())
}
