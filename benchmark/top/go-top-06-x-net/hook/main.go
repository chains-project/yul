package main

import (
	"fmt"
	"log"
	"net/http"

	"golang.org/x/net/http2"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "hello over %s\n", r.Proto)
	})

	srv := &http.Server{
		Addr:    ":8443",
		Handler: mux,
	}

	if err := http2.ConfigureServer(srv, &http2.Server{}); err != nil {
		log.Fatal(err)
	}

	log.Println("listening on", srv.Addr)
	log.Fatal(srv.ListenAndServeTLS("cert.pem", "key.pem"))
}
