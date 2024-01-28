package writers

import (
	"fmt"

	"strconv"

	"gocv.io/x/gocv"
)

type FileWriter struct {
	Prefix string
}

func openNewCatpure(filename string, cols, rows int) (*gocv.VideoWriter, error) {
	writer, err := gocv.VideoWriterFile(filename, "MJPG", 25, cols, rows, true)
	if err != nil {
		fmt.Printf("error opening video writer device: %v\n", filename)
		return nil, err
	}
	return writer, nil
}

func (w FileWriter) Write(imgs <-chan gocv.Mat) (int, error) {
	img := <-imgs // first frame

	if img.Empty() {
		return 0, nil
	}

	numBuffs := 0
	buffSize := 100
	cnt := 0
	filename := "/tmp/" + w.Prefix + "_" + strconv.Itoa(numBuffs) + ".avi"
	fmt.Println("filename: " + filename)
	writer, err := openNewCatpure(filename, img.Cols(), img.Rows())
	if err != nil {
		fmt.Printf("error opening video writer device: %v\n", filename)
		return 0, err
	}
	// defer writer.Close()

	for img := range imgs {
		if img.Empty() {
			continue
		}
		writer.Write(img)
		cnt += 1
		if cnt%buffSize == 0 {
			fmt.Println("opening new...")
			writer.Close()
			numBuffs += 1
			filename = "/tmp/" + w.Prefix + "_" + strconv.Itoa(numBuffs) + ".avi"
			writer, err = openNewCatpure(filename, img.Cols(), img.Rows())
			if err != nil {
				fmt.Printf("error opening video writer device: %v\n", filename)
				return 0, err
			}
		}
	}
	fmt.Println("DONE after " + strconv.Itoa(cnt))
	writer.Close()
	return cnt, nil
}
