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
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		w.Write([]byte("ok\n"))
	})

	h2s := &http2.Server{}
	handler := h2c.NewHandler(mux, h2s)

	log.Println("listening on :8080 (h2c)")
	log.Fatal(http.ListenAndServe(":8080", handler))
}
