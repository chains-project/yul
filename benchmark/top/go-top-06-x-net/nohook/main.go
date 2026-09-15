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
		fmt.Fprintf(w, "protocol: %s\n", r.Proto)
	})

	server := &http.Server{
		Addr:    ":8443",
		Handler: mux,
	}

	if err := http2.ConfigureServer(server, &http2.Server{}); err != nil {
		log.Fatalf("configuring http2: %v", err)
	}

	log.Println("listening on :8443")
	log.Fatal(server.ListenAndServeTLS("cert.pem", "key.pem"))
}
