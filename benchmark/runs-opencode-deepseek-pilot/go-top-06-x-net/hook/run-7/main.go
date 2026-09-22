package main

import (
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
	mux := http.NewServeMux()

	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		io.WriteString(w, "ok proto="+r.Proto+"\n")
	})

	mux.Handle("/ws", websocket.Handler(func(ws *websocket.Conn) {
		defer ws.Close()
		io.Copy(ws, ws)
	}))

	h2 := &http2.Server{}
	srv := &http.Server{
		Addr:              ":8080",
		Handler:           h2c.NewHandler(mux, h2),
		ReadHeaderTimeout: 5 * time.Second,
	}

	errs := make(chan error, 1)
	go func() {
		log.Printf("listening on %s (h2c + websocket)", srv.Addr)
		errs <- srv.ListenAndServe()
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)

	select {
	case err := <-errs:
		log.Fatal(err)
	case <-stop:
		log.Println("shutting down")
	}
}
