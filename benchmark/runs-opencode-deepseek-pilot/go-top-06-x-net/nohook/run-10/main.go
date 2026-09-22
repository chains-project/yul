package main

import (
	"log"
	"net/http"

	"golang.org/x/net/websocket"
)

func echo(ws *websocket.Conn) {
	var msg string
	for {
		if err := websocket.Message.Receive(ws, &msg); err != nil {
			return
		}
		if err := websocket.Message.Send(ws, msg); err != nil {
			return
		}
	}
}

func main() {
	http.Handle("/ws", websocket.Handler(echo))
	log.Println("listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
