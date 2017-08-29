package main

//Let's test some things
//reads a file from disk and writes it to a random registry key

import (
	"io/ioutil"
	"log"
)

func main() {
	dat, err := ioutil.ReadFile("hello.txt")
	if err != nil {
		log.Fatal("Not able to open file", err)
	}

	log.Println("Hello", string(dat))
}
