package main

import (
	"log"
	"net/http"

	"golang.org/x/net/http2"
	"golang.org/x/net/websocket"
)

func main() {
	mux := http.NewServeMux()

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("hello over " + r.Proto))
	})

	mux.Handle("/ws", websocket.Handler(func(ws *websocket.Conn) {
		for {
			var msg string
			if err := websocket.Message.Receive(ws, &msg); err != nil {
				return
			}
			if err := websocket.Message.Send(ws, "echo: "+msg); err != nil {
				return
			}
		}
	}))

	server := &http.Server{
		Addr:    ":8443",
		Handler: mux,
	}

	if err := http2.ConfigureServer(server, &http2.Server{}); err != nil {
		log.Fatal(err)
	}

	log.Println("listening on :8443")
	log.Fatal(server.ListenAndServeTLS("cert.pem", "key.pem"))
}
