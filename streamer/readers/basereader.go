package readers

import "gocv.io/x/gocv"

type FrameReader interface {
	Read(chan<- gocv.Mat) (int, error)
}
