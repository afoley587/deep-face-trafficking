package main

import (
	"fmt"
	"log"
	"sync"
	"testing"

	"gocv.io/x/gocv"
)

func processVideo(wg *sync.WaitGroup, id int, file string) {
	defer wg.Done()

	// Open the video capture
	cap, err := gocv.OpenVideoCapture(file)
	if err != nil {
		log.Printf("Error opening video capture %d: %v\n", id, err)
		return
	}

	defer cap.Close()

	frame := gocv.NewMat()
	defer frame.Close()

	fr := 0
	for {
		// Read a frame from the video capture
		if ok := cap.Read(&frame); !ok || frame.Empty() {
			break
		}
		fr++

		// Here you can process the frame if needed
		// e.g., gocv.CvtColor(frame, &gray, gocv.ColorBGRToGray)
	}
}

func TestOne(t *testing.T) {
	videoFiles := makeSlice(1)
	runner(videoFiles)
}

// func TestFifty(t *testing.T) {
// 	videoFiles := makeSlice(50)
// 	runner(videoFiles)
// }

// func TestOneHundred(t *testing.T) {
// 	videoFiles := makeSlice(100)
// 	runner(videoFiles)
// }

// func TestOneHundredFifty(t *testing.T) {
// 	videoFiles := makeSlice(150)
// 	runner(videoFiles)
// }

// func TestTwoHundred(t *testing.T) {
// 	videoFiles := makeSlice(200)
// 	runner(videoFiles)
// }

// func TestThreeHundred(t *testing.T) {
// 	videoFiles := makeSlice(300)
// 	runner(videoFiles)
// }

// func TestFourHundred(t *testing.T) {
// 	videoFiles := makeSlice(400)
// 	runner(videoFiles)
// }

// func TestFiveHundred(t *testing.T) {
// 	videoFiles := makeSlice(500)
// 	runner(videoFiles)
// }

func TestOneThousand(t *testing.T) {
	videoFiles := makeSlice(1000)
	runner(videoFiles)
}

func TestTwoThousand(t *testing.T) {
	videoFiles := makeSlice(1000)
	runner(videoFiles)
}

func makeSlice(n int) []string {
	videoFiles := make([]string, n)
	for i := 0; i < n; i++ {
		videoFiles[i] = "test.mp4"
	}
	return videoFiles
}

func runner(vf []string) {

	var wg sync.WaitGroup

	// Start a goroutine for each video file
	for i, file := range vf {
		wg.Add(1)
		go processVideo(&wg, i, file)
	}

	// Wait for all goroutines to finish
	wg.Wait()

	fmt.Println("All video captures have been processed.")
}
