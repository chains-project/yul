package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"nhooyr.io/websocket"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/api", handleAPI)
	mux.HandleFunc("/ws", handleWebSocket)

	server := &http.Server{
		Addr:    ":8080",
		Handler: h2c.NewHandler(mux, &http2.Server{}),
	}

	log.Printf("Server starting on :8080")
	if err := server.ListenAndServe(); err != http.ErrServerClosed {
		log.Fatalf("Server failed: %v", err)
	}
}

func handleAPI(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello from HTTP/2 server")
}

func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	c, err := websocket.Accept(w, r, nil)
	if err != nil {
		log.Printf("WebSocket upgrade failed: %v", err)
		return
	}
	defer c.Close(websocket.StatusInternalServerError, "server error")

	ctx, cancel := context.WithTimeout(r.Context(), 10*time.Second)
	defer cancel()

	msg, err := c.Receive(ctx)
	if err != nil {
		log.Printf("Receive failed: %v", err)
		return
	}
	c.Close(websocket.StatusNormalClosure, "")
}