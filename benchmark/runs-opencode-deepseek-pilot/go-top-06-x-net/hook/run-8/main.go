package main

import (
	"log"
	"net/http"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("hello over http/2\n"))
	})

	h2s := &http2.Server{}
	handler := h2c.NewHandler(mux, h2s)

	addr := ":8080"
	log.Printf("listening on %s (h2c)", addr)
	log.Fatal(http.ListenAndServe(addr, handler))
}
