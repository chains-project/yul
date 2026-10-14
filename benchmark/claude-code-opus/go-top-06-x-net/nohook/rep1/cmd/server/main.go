// Command server is a minimal HTTP server that serves HTTP/2 over cleartext
// (h2c) alongside a websocket echo endpoint.
package main

import (
	"io"
	"log"
	"net/http"
	"os"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func main() {
	addr := os.Getenv("ADDR")
	if addr == "" {
		addr = ":8080"
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		io.WriteString(w, "hello over "+r.Proto+"\n")
	})
	mux.Handle("/ws", websocket.Handler(func(ws *websocket.Conn) {
		io.Copy(ws, ws) // echo
	}))

	srv := &http.Server{
		Addr:    addr,
		Handler: h2c.NewHandler(mux, &http2.Server{}),
	}
	log.Printf("listening on %s", addr)
	log.Fatal(srv.ListenAndServe())
}
