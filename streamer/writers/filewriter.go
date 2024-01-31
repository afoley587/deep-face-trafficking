package writers

import (
	"fmt"

	"strconv"

	"gocv.io/x/gocv"
)

type FileWriter struct {
	Prefix string
}

func (w FileWriter) Write(imgs <-chan gocv.Mat, size int) (int, error) {
	img := <-imgs // first frame

	if img.Empty() {
		return 0, nil
	}

	batchPref := "/tmp/" + w.Prefix
	fchan := make(chan string)
	done := make(chan WriterGoroutineResult)

	go batchToFile(fchan, done, imgs, batchPref, size, img.Cols(), img.Rows())

	go func() {
		for fname := range fchan {
			fmt.Println("File " + fname + " finished")
		}
	}()

	res := <-done
	close(fchan)
	close(done)
	fmt.Println("DONE after " + strconv.Itoa(res.Count))
	return res.Count, res.Error
}
