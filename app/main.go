package main

import (
	"fmt"
	"log"
	"net/http"
	"os/exec"
)

// index là handler đơn giản để demo
func index(w http.ResponseWriter, r *http.Request) {
	// Demo SAST: pattern khiến Semgrep báo (rule go.os.exec.command-injection) → pipeline fail, có report mẫu
	cmd := r.URL.Query().Get("cmd")
	if cmd == "" {
		cmd = "echo hello"
	}
	_ = exec.Command("sh", "-c", cmd) // chưa gọi .Run(), chỉ để sinh finding cho report mẫu
	fmt.Fprintln(w, "Hello from Go CI/CD + SAST demo!")
}

func main() {
	http.HandleFunc("/", index)
	log.Println("Starting Go server on :8000")
	log.Fatal(http.ListenAndServe(":8000", nil))
}

