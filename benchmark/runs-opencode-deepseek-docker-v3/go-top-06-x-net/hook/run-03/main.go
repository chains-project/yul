package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/coder/websocket"
	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
)

func main() {
	addr := ":8080"
	if v := os.Getenv("ADDR"); v != "" {
		addr = v
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/ws", echo)
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.Error(w, "not found", http.StatusNotFound)
	})

	h2s := &http2.Server{}
	srv := &http.Server{
		Addr:              addr,
		Handler:           h2c.NewHandler(mux, h2s),
		ReadHeaderTimeout: 5 * time.Second,
	}

	log.Printf("listening on %s (h2c + websocket echo at /ws)", addr)
	if err := srv.ListenAndServe(); err != nil {
		log.Fatal(err)
	}
}

func echo(w http.ResponseWriter, r *http.Request) {
	c, err := websocket.Accept(w, r, &websocket.AcceptOptions{
		InsecureSkipVerify: true,
	})
	if err != nil {
		log.Printf("accept: %v", err)
		return
	}
	defer c.CloseNow()

	ctx, cancel := context.WithTimeout(r.Context(), time.Hour)
	defer cancel()

	for {
		typ, data, err := c.Read(ctx)
		if err != nil {
			c.Close(websocket.StatusNormalClosure, "")
			return
		}
		if err := c.Write(ctx, typ, data); err != nil {
			log.Printf("write: %v", err)
			return
		}
	}
}
