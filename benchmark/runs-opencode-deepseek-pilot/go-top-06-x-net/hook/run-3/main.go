package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/websocket"
)

func main() {
	mux := http.NewServeMux()

	mux.Handle("/ws", websocket.Handler(func(conn *websocket.Conn) {
		conn.Write([]byte("hello from websocket"))
	}))

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "hello over http/2")
	})

	srv := &http.Server{
		Addr:    ":8080",
		Handler: mux,
	}

	h2 := &http2.Server{}
	if err := http2.ConfigureServer(srv, h2); err != nil {
		log.Fatalf("configure http/2 server: %v", err)
	}

	go func() {
		log.Println("listening on :8080 (h2c + websocket)")
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("serve: %v", err)
		}
	}()

	time.Sleep(100 * time.Millisecond)

	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("shutdown: %v", err)
	}
}
