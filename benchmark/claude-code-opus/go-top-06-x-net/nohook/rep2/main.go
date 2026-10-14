// Command netapp is a network server built on golang.org/x/net, providing
// HTTP/2 (including cleartext h2c) and websocket support.
package main

import (
	"flag"
	"fmt"
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
		fmt.Fprintf(w, "hello over %s\n", r.Proto)
	})
	mux.Handle("/ws", websocket.Handler(echo))

	srv := &http.Server{
		Addr:              *addr,
		Handler:           h2c.NewHandler(mux, &http2.Server{}),
		ReadHeaderTimeout: 10 * time.Second,
	}

	log.Printf("listening on %s (HTTP/1.1, h2c, websocket at /ws)", *addr)
	log.Fatal(srv.ListenAndServe())
}

// echo writes every websocket message back to the sender.
func echo(ws *websocket.Conn) {
	defer ws.Close()
	for {
		var msg string
		if err := websocket.Message.Receive(ws, &msg); err != nil {
			return
		}
		if err := websocket.Message.Send(ws, msg); err != nil {
			return
		}
	}
}
