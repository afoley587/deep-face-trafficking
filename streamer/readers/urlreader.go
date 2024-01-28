package readers

import (
	"fmt"

	"gocv.io/x/gocv"
)

type UrlReader struct {
	Url string
}

func (r UrlReader) Read(imgs chan<- gocv.Mat, done chan<- int) (int, error) {
	read := 0
	still_reading := true

	stream, err := gocv.OpenVideoCapture(r.Url)

	if err != nil {
		fmt.Println(err)
		done <- read
		return 0, err
	}
	img := gocv.NewMat()

	for {
		still_reading = stream.Read(&img)
		if !still_reading {
			break
		}
		imgs <- img
		read++
	}
	done <- read
	return read, nil
}
