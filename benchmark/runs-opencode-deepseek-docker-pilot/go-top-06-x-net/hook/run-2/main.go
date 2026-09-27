package main

import (
	"log"
	"net/http"

	"github.com/gorilla/websocket"
	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
}

func echo(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("websocket upgrade: %v", err)
		return
	}
	defer conn.Close()

	for {
		mt, msg, err := conn.ReadMessage()
		if err != nil {
			return
		}
		if err := conn.WriteMessage(mt, msg); err != nil {
			return
		}
	}
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/echo", echo)
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.Write([]byte("ok"))
	})

	h2s := &http2.Server{}
	srv := &http.Server{
		Addr:    ":8080",
		Handler: h2c.NewHandler(mux, h2s),
	}

	log.Printf("listening on %s (h2c + websockets)", srv.Addr)
	log.Fatal(srv.ListenAndServe())
}
