// Command server runs an HTTP server that speaks HTTP/1.1, HTTP/2 over
// cleartext (h2c), and websockets on the same port.
package main

import (
	"flag"
	"io"
	"log"
	"net/http"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func main() {
	addr := flag.String("addr", ":8080", "listen address")
	flag.Parse()

	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		io.WriteString(w, "hello over "+r.Proto+"\n")
	})
	// Echoes every websocket message back to the sender.
	mux.Handle("/ws", websocket.Handler(func(ws *websocket.Conn) {
		io.Copy(ws, ws)
	}))

	srv := &http.Server{
		Addr:              *addr,
		Handler:           h2c.NewHandler(mux, &http2.Server{}),
		ReadHeaderTimeout: 10 * time.Second,
	}
	log.Printf("listening on %s", *addr)
	log.Fatal(srv.ListenAndServe())
}
