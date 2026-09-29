package main

import (
	"context"
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
	mux.HandleFunc("/", index)

	addr := ":8080"
	if v := os.Getenv("ADDR"); v != "" {
		addr = v
	}

	srv := &http.Server{
		Addr: addr,
		Handler: h2c.NewHandler(mux, &http2.Server{}),
	}

	go func() {
		log.Printf("listening on %s (HTTP/2 cleartext + websocket)", addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("server error: %v", err)
		}
	}()

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	<-ctx.Done()

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(shutdownCtx); err != nil {
		log.Printf("shutdown error: %v", err)
	}
}

func index(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.Write([]byte("hello over " + r.Proto + "\n"))
}

func echo(ws *websocket.Conn) {
	defer ws.Close()
	buf := make([]byte, 4096)
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
