package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/coder/websocket"
)

func main() {
	addr := flag.String("addr", ":8080", "address to listen on")
	certFile := flag.String("cert", "", "TLS certificate file; enables HTTPS with HTTP/2")
	keyFile := flag.String("key", "", "TLS private key file")
	flag.Parse()

	mux := http.NewServeMux()
	mux.HandleFunc("/", handleIndex)
	mux.HandleFunc("/h2", handleProto)
	mux.HandleFunc("/ws", handleWS)

	protocols := new(http.Protocols)
	protocols.SetHTTP1(true)
	protocols.SetHTTP2(true)
	protocols.SetUnencryptedHTTP2(true)

	srv := &http.Server{
		Addr:              *addr,
		Handler:           mux,
		Protocols:         protocols,
		ReadHeaderTimeout: 5 * time.Second,
		IdleTimeout:       60 * time.Second,
		ErrorLog:          log.New(os.Stderr, "http: ", log.LstdFlags),
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	errCh := make(chan error, 1)
	go func() {
		if *certFile != "" && *keyFile != "" {
			log.Printf("listening on %s (https, h2 + h2c)", *addr)
			errCh <- srv.ListenAndServeTLS(*certFile, *keyFile)
			return
		}
		log.Printf("listening on %s (http, h2c)", *addr)
		errCh <- srv.ListenAndServe()
	}()

	select {
	case err := <-errCh:
		if err != nil && err != http.ErrServerClosed {
			log.Fatalf("serve: %v", err)
		}
	case <-ctx.Done():
		log.Print("shutting down")
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		if err := srv.Shutdown(shutdownCtx); err != nil {
			log.Printf("shutdown: %v", err)
		}
	}
}

func handleIndex(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "netapp is running\nprotocol: %s\n", r.Proto)
}

func handleProto(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	fmt.Fprintf(w, "{\"proto\":%q,\"http2\":%t}\n", r.Proto, r.ProtoMajor == 2)
}

func handleWS(w http.ResponseWriter, r *http.Request) {
	c, err := websocket.Accept(w, r, &websocket.AcceptOptions{
		InsecureSkipVerify: true,
	})
	if err != nil {
		log.Printf("websocket accept: %v", err)
		return
	}
	defer c.CloseNow()

	ctx := r.Context()
	for {
		typ, data, err := c.Read(ctx)
		if err != nil {
			return
		}
		if err := c.Write(ctx, typ, data); err != nil {
			return
		}
	}
}
