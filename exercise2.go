// Go 1.2
// go run helloworld_go.go

package main

import (
    "fmt"
    "runtime"
  //  "time"
)

//var i int


func increase(resource1 chan int32, done chan string) {
	 var i int32

     for j := 0 ; j < 1000000 ; j++{
	 i = <- resource1
     i=i+1
	 resource1 <- i
     }

	done <- "Increase task"
}
func decrease(resource1 chan int32, done chan string) {
	 var i int32

     for j := 0 ; j < 1000000-1 ; j++{
	 i = <- resource1
     i=i-1
	 resource1 <- i
     }
	done <- "Decrease task"
}
func main() {
	
	resource1 := make(chan int32, 1)
	done	  := make(chan string)

	
	resource1 <- 0

    runtime.GOMAXPROCS(runtime.NumCPU())    // I guess this is a hint to what GOMAXPROCS does...
                                            // Try doing the exercise both with and without it!
    go increase(resource1, done)                      // This spawns someGoroutine() as a 	goroutine
    go decrease(resource1, done)

    // We have no way to wait for the completion of a goroutine (without additional syncronization of some sort)
    // We'll come back to using channels in Exercise 2. For now: Sleep.
  	 // time.Sleep(100*time.Millisecond)
	for j := 0 ; j < 2 ; j++{
		select {
			case msg := <-done:
				fmt.Println("Finished task:", msg);
		}
	}
	
	fmt.Printf("Finish:\n")
    fmt.Printf("Final value of resource = %d\n",<-resource1)
}
