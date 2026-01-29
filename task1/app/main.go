package main

import (
	"fmt"
	"log"
	"net/http"
)

// index là handler đơn giản để demo
func index(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Hello from Go CI/CD + SAST demo!")
}

func main() {
	http.HandleFunc("/", index)
	log.Println("Starting Go server on :8000")
	log.Fatal(http.ListenAndServe(":8000", nil))
}

