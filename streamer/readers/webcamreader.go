package readers

import (
	"gocv.io/x/gocv"
)

type WebcamReader struct {
	Device int
}

func (r WebcamReader) Read(imgs chan<- gocv.Mat, done chan<- int) (int, error) {
	read := 0
	still_reading := true

	webcam, _ := gocv.VideoCaptureDevice(r.Device)
	img := gocv.NewMat()

	for {
		still_reading = webcam.Read(&img)
		if !still_reading || read > 500 {
			break
		}
		imgs <- img
		read++
	}

	done <- read
	webcam.Close()
	return read, nil
}
