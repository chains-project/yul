package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func main() {
	mux := http.NewServeMux()
	mux.Handle("/ws", websocket.Handler(echo))
	mux.HandleFunc("/", index)

	handler := h2c.NewHandler(mux, &http2.Server{})

	srv := &http.Server{
		Addr:              ":8080",
		Handler:           handler,
		ReadHeaderTimeout: 5 * time.Second,
	}

	go func() {
		log.Printf("listening on %s", srv.Addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("server error: %v", err)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("shutdown error: %v", err)
	}
}

func index(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Write([]byte("http/2 + websocket server\n"))
}

func echo(ws *websocket.Conn) {
	defer ws.Close()
	buf := make([]byte, 1024)
	for {
		n, err := ws.Read(buf)
		if err != nil {
			return
		}
		if _, err := ws.Write(buf[:n]); err != nil {
			return
		}
	}
}
