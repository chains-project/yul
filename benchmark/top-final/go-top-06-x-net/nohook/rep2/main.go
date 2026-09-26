package main

import (
	"fmt"
	"log"
	"net/http"

	"golang.org/x/net/http2"
	"golang.org/x/net/http2/h2c"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "proto=%s method=%s path=%s\n", r.Proto, r.Method, r.URL.Path)
	})

	h2s := &http2.Server{}
	server := &http.Server{
		Addr:    ":8080",
		Handler: h2c.NewHandler(mux, h2s),
	}

	log.Println("listening on :8080 (h2c)")
	log.Fatal(server.ListenAndServe())
}
