// Package netapp wires together the extended networking primitives used by
// the application: cleartext HTTP/2 and websockets.
package netapp

import (
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"

	"golang.org/x/net/websocket"
)

// Server is the application's HTTP handler set.
type Server struct {
	mux *http.ServeMux
}

// New returns a Server with all routes registered.
func New() *Server {
	s := &Server{mux: http.NewServeMux()}
	s.routes()
	return s
}

// Handler exposes the underlying http.Handler so callers can wrap it (for
// example with h2c) or mount it in an existing server.
func (s *Server) Handler() http.Handler { return s.mux }

func (s *Server) routes() {
	s.mux.HandleFunc("GET /healthz", s.handleHealth)
	s.mux.Handle("GET /ws", websocket.Handler(s.handleWebSocket))
}

// handleHealth reports the negotiated protocol version so clients can verify
// whether HTTP/2 was used.
func (s *Server) handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(map[string]string{
		"status":  "ok",
		"proto":   r.Proto,
		"version": fmt.Sprintf("%d.%d", r.ProtoMajor, r.ProtoMinor),
	})
}

// handleWebSocket echoes every message back to the client until the peer
// closes the connection.
func (s *Server) handleWebSocket(conn *websocket.Conn) {
	defer conn.Close()
	if _, err := io.Copy(conn, conn); err != nil {
		slog.Debug("websocket closed", "remote", conn.RemoteAddr(), "err", err)
	}
}
