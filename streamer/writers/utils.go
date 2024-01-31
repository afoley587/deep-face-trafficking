package writers

import (
	"fmt"
	"strconv"

	"gocv.io/x/gocv"
)

func openVideoWriterFile(filename string, cols, rows int) (*gocv.VideoWriter, error) {
	writer, err := gocv.VideoWriterFile(filename, "MJPG", 25, cols, rows, true)
	if err != nil {
		fmt.Printf("error opening video writer device: %v\n", filename)
		return nil, err
	}
	return writer, nil
}

func batchToFile(fchan chan<- string, done chan<- WriterGoroutineResult, imgs <-chan gocv.Mat, prefix string, size, cols, rows int) {
	cnt := 0
	buffs := 0
	filename := prefix + "_" + strconv.Itoa(buffs) + ".avi"
	writer, err := openVideoWriterFile(filename, cols, rows)
	res := WriterGoroutineResult{Count: 0, Error: nil}
	if err != nil {
		fmt.Printf("error opening video writer device: %v\n", filename)
		res.Error = err
		done <- res
		return
	}

	for img := range imgs {
		if img.Empty() {
			continue
		}
		writer.Write(img)
		cnt += 1
		if cnt%size == 0 {
			fchan <- filename
			fmt.Println("opening new...")
			writer.Close()
			buffs += 1
			filename = prefix + "_" + strconv.Itoa(buffs) + ".avi"
			writer, err = openVideoWriterFile(filename, img.Cols(), img.Rows())
			if err != nil {
				fmt.Printf("error opening video writer device: %v\n", filename)
				res.Error = err
				done <- res
				return
			}
		}
	}

	fchan <- filename
	res.Count = cnt
	done <- res
	writer.Close()
}
