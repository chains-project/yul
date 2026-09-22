package main

import (
	"log"
	"net/http"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func main() {
	mux := http.NewServeMux()

	mux.Handle("/ws", websocket.Handler(func(ws *websocket.Conn) {
		websocket.Message.Send(ws, "hello from websocket")
	}))

	srv := &http.Server{
		Addr:    ":8080",
		Handler: h2c.NewHandler(mux, &http2.Server{}),
	}

	log.Println("listening on", srv.Addr)
	if err := srv.ListenAndServe(); err != nil {
		log.Fatal(err)
	}
}
