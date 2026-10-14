// Command server is the entry point for the network application.
package main

import (
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func main() {
	addr := flag.String("addr", ":8080", "listen address")
	flag.Parse()

	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "hello over %s\n", r.Proto)
	})
	mux.Handle("/ws", websocket.Handler(func(ws *websocket.Conn) {
		io.Copy(ws, ws) // echo
	}))

	// h2c serves HTTP/2 over cleartext alongside HTTP/1.1.
	srv := &http.Server{
		Addr:    *addr,
		Handler: h2c.NewHandler(mux, &http2.Server{}),
	}
	log.Printf("listening on %s", *addr)
	log.Fatal(srv.ListenAndServe())
}
