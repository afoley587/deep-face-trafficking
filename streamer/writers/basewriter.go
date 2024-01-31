package writers

import "gocv.io/x/gocv"

type FrameWriter interface {
	Write(<-chan gocv.Mat, int) (int, error)
}
