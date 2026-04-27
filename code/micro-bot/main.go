// main.go
package main

import (
	"net/http"
	"strings"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

func main() {
	http.Handle("/", http.FileServer(http.Dir("./static")))
	http.HandleFunc("/ws", ws)

	http.ListenAndServe(":5013", nil)
}

func ws(w http.ResponseWriter, r *http.Request) {
	c, _ := upgrader.Upgrade(w, r, nil)
	defer c.Close()

	for {
		_, msg, err := c.ReadMessage()
		if err != nil {
			break
		}

		q := strings.ToLower(string(msg))
		ans := "unknown"

		if strings.Contains(q, "api") {
			ans = "API = communication layer"
		} else if strings.Contains(q, "service") {
			ans = "independent deployable unit"
		} else if strings.Contains(q, "docker") {
			ans = "container runtime"
		} else if strings.Contains(q, "kubernetes") {
			ans = "container orchestrator"
		}

		c.WriteMessage(websocket.TextMessage, []byte(ans))
	}
}