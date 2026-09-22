package main

import (
	"context"
	"flag"
	"fmt"
	"io"
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
	addr := flag.String("addr", ":8080", "address to listen on")
	flag.Parse()

	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "hello from %s over %s\n", r.Host, r.Proto)
	})
	mux.Handle("/echo", websocket.Handler(func(ws *websocket.Conn) {
		defer ws.Close()
		if _, err := io.Copy(ws, ws); err != nil {
			log.Printf("websocket echo: %v", err)
		}
	}))

	h2s := &http2.Server{}
	server := &http.Server{
		Addr:    *addr,
		Handler: h2c.NewHandler(mux, h2s),
	}

	go func() {
		log.Printf("listening on %s (h2c + websockets)", *addr)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("server: %v", err)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := server.Shutdown(ctx); err != nil {
		log.Printf("shutdown: %v", err)
	}
}
