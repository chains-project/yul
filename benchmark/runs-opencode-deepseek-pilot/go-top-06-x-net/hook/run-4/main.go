package main

import (
	"context"
	"flag"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

type app struct{}

func (a *app) routes() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", a.health)
	mux.Handle("/ws", websocket.Handler(a.echo))
	return mux
}

func (a *app) health(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/plain; charset=utf-8")
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("ok\n"))
}

func (a *app) echo(ws *websocket.Conn) {
	defer ws.Close()
	_, _ = ws.Write([]byte("connected\n"))
	buf := make([]byte, 4096)
	for {
		n, err := ws.Read(buf)
		if n > 0 {
			if _, werr := ws.Write(buf[:n]); werr != nil {
				return
			}
		}
		if err != nil {
			return
		}
	}
}

func main() {
	addr := flag.String("addr", ":8443", "address to listen on")
	certFile := flag.String("cert", "", "TLS certificate file (enables HTTPS + HTTP/2)")
	keyFile := flag.String("key", "", "TLS key file (enables HTTPS + HTTP/2)")
	flag.Parse()

	a := &app{}
	srv := &http.Server{
		Addr:              *addr,
		Handler:           a.routes(),
		ReadHeaderTimeout: 10 * time.Second,
	}

	if *certFile == "" || *keyFile == "" {
		srv.Handler = h2c.NewHandler(srv.Handler, &http2.Server{})
	}

	errCh := make(chan error, 1)
	go func() {
		if *certFile != "" && *keyFile != "" {
			if err := http2.ConfigureServer(srv, &http2.Server{}); err != nil {
				errCh <- err
				return
			}
			errCh <- srv.ListenAndServeTLS(*certFile, *keyFile)
			return
		}
		errCh <- srv.ListenAndServe()
	}()

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()

	select {
	case err := <-errCh:
		if err != nil && err != http.ErrServerClosed {
			log.Fatalf("server error: %v", err)
		}
	case <-ctx.Done():
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		if err := srv.Shutdown(shutdownCtx); err != nil {
			log.Printf("graceful shutdown failed: %v", err)
		}
	}
}
