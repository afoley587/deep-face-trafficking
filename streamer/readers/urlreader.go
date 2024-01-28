package readers

import (
	"gocv.io/x/gocv"
)

type UrlReader struct {
	Url string
}

func (r UrlReader) Read(imgs chan<- gocv.Mat) (int, error) {
	read := 0
	still_reading := true

	stream, _ := gocv.OpenVideoCapture(r.Url)
	img := gocv.NewMat()

	for {
		still_reading = stream.Read(&img)
		if !still_reading {
			break
		}
		imgs <- img
		read++
	}
	return read, nil
}
