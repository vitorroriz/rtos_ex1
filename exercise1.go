// Go 1.2
// go run helloworld_go.go

package main

import (
    "fmt"
    "runtime"
    "time"
)

var i int

func increase() {
     for j := 0 ; j < 1000000 ; j++{
     i=i+1
     }
}
func decrease() {
     for j := 0 ; j < 1000000 ; j++{
     i=i-1
     }
}
func main() {
    runtime.GOMAXPROCS(runtime.NumCPU())    // I guess this is a hint to what GOMAXPROCS does...
                                            // Try doing the exercise both with and without it!
    go increase()                      // This spawns someGoroutine() as a goroutine
    go decrease()

    // We have no way to wait for the completion of a goroutine (without additional syncronization of some sort)
    // We'll come back to using channels in Exercise 2. For now: Sleep.
    time.Sleep(100*time.Millisecond)
    fmt.Printf("%d\n",i)
}