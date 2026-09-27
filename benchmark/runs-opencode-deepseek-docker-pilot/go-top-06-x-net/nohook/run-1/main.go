package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func main() {
	mux := http.NewServeMux()
	mux.Handle("/ws", websocket.Handler(echo))
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "proto=%s\n", r.Proto)
	})

	srv := &http.Server{
		Addr:    ":8080",
		Handler: h2c.NewHandler(mux, &http2.Server{}),
	}

	go func() {
		log.Printf("listening on %s (h2c + websocket)", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal(err)
		}
	}()

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	<-ctx.Done()

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = srv.Shutdown(shutdownCtx)
}

func echo(ws *websocket.Conn) {
	defer ws.Close()
	_, _ = io.Copy(ws, ws)
}
