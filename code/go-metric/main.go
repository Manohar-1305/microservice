package main

import (
        "encoding/json"
        "net/http"
        "sort"
        "sync"
        "time"
)

type Counter struct {
        mu        sync.Mutex
        total     int
        routes    map[string]int
        timeline  []int
        lastTotal int
}

var counter = Counter{
        routes: make(map[string]int),
}

func (c *Counter) Inc(path string) {
        c.mu.Lock()
        defer c.mu.Unlock()
        c.total++
        c.routes[path]++
}

func (c *Counter) Snapshot() {
        c.mu.Lock()
        defer c.mu.Unlock()

        diff := c.total - c.lastTotal
        c.timeline = append(c.timeline, diff)

        if len(c.timeline) > 20 {
                c.timeline = c.timeline[1:]
        }

        c.lastTotal = c.total
}

func (c *Counter) GetStats() map[string]interface{} {
        c.mu.Lock()
        defer c.mu.Unlock()

        type kv struct {
                Key   string
                Value int
        }
        var sorted []kv
        for k, v := range c.routes {
                sorted = append(sorted, kv{k, v})
        }
        sort.Slice(sorted, func(i, j int) bool {
                return sorted[i].Value > sorted[j].Value
        })

        return map[string]interface{}{
                "total":    c.total,
                "routes":   c.routes,
                "top":      sorted,
                "timeline": c.timeline,
        }
}

func statsAPI(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(counter.GetStats())
}

func middleware(next http.HandlerFunc) http.HandlerFunc {
        return func(w http.ResponseWriter, r *http.Request) {
                counter.Inc(r.URL.Path)
                next(w, r)
        }
}

func handler(name string) http.HandlerFunc {
        return func(w http.ResponseWriter, r *http.Request) {
                w.Write([]byte(name + " service"))
        }
}

func startTimeline() {
        for {
                time.Sleep(3 * time.Second)
                counter.Snapshot()
        }
}

func hitAPI(w http.ResponseWriter, r *http.Request) {
        path := r.URL.Query().Get("service")
        if path == "" {
                http.Error(w, "missing service", 400)
                return
        }

        counter.Inc(path)
        w.WriteHeader(http.StatusOK)
}

func main() {
        go startTimeline()

        http.HandleFunc("/home", middleware(handler("home")))
        http.HandleFunc("/audio", middleware(handler("audio")))
        http.HandleFunc("/music", middleware(handler("music")))
        http.HandleFunc("/pdf", middleware(handler("pdf")))
        http.HandleFunc("/word_to_pdf", middleware(handler("word_to_pdf")))
        http.HandleFunc("/youtube", middleware(handler("youtube")))
        http.HandleFunc("/shortener", middleware(handler("shortener")))
        http.HandleFunc("/todo", middleware(handler("todo")))
        http.HandleFunc("/audio-combiner", middleware(handler("audio-combiner")))
        http.HandleFunc("/audio-cutter", middleware(handler("audio-cutter")))
        http.HandleFunc("/cidr", middleware(handler("cidr")))

        http.HandleFunc("/api/stats", statsAPI)

        http.HandleFunc("/api/hit", hitAPI)

        http.Handle("/", http.FileServer(http.Dir("./static")))

        http.ListenAndServe(":5012", nil)
}
