package main

import (
	"io"
	"log"
	"net/http"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
	"golang.org/x/net/websocket"
)

func echo(ws *websocket.Conn) {
	if _, err := io.Copy(ws, ws); err != nil {
		log.Printf("websocket: %v", err)
	}
}

func main() {
	mux := http.NewServeMux()
	mux.Handle("/ws", websocket.Handler(echo))
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		io.WriteString(w, "ok\n")
	})

	srv := &http.Server{
		Addr:    ":8080",
		Handler: h2c.NewHandler(mux, &http2.Server{}),
	}

	log.Println("listening on :8080 (h2c + websocket)")
	if err := srv.ListenAndServe(); err != nil {
		log.Fatal(err)
	}
}
