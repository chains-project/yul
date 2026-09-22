package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func wsHandler(ws *websocket.Conn) {
	var msg string
	if err := websocket.Message.Receive(ws, &msg); err != nil {
		log.Printf("websocket receive: %v", err)
		return
	}
	if err := websocket.Message.Send(ws, "echo: "+msg); err != nil {
		log.Printf("websocket send: %v", err)
	}
}

func main() {
	mux := http.NewServeMux()
	mux.Handle("/ws", websocket.Handler(wsHandler))
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "hello over %s\n", r.Proto)
	})

	srv := &http.Server{
		Addr:    ":8080",
		Handler: h2c.NewHandler(mux, &http2.Server{}),
	}

	go func() {
		log.Printf("listening on %s (HTTP/1.1, h2c, websockets)", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("server: %v", err)
		}
	}()

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	<-ctx.Done()

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = srv.Shutdown(shutdownCtx)
}
