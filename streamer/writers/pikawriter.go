package writers

import (
	"context"
	"fmt"
	"log"
	"time"

	"strconv"

	amqp "github.com/rabbitmq/amqp091-go"
	"gocv.io/x/gocv"
)

type PikaWriter struct {
	Topic    string
	Exchange string
}

func (w PikaWriter) Write(imgs <-chan gocv.Mat) (int, error) {
	img := <-imgs // first frame

	if img.Empty() {
		return 0, nil
	}

	numBuffs := 0
	buffSize := 100
	cnt := 0
	filename := "/tmp/" + w.Topic + "_" + strconv.Itoa(numBuffs) + ".avi"
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
			filename = "/tmp/" + w.Topic + "_" + strconv.Itoa(numBuffs) + ".avi"
			writer, err = openNewCatpure(filename, img.Cols(), img.Rows())
			if err != nil {
				fmt.Printf("error opening video writer device: %v\n", filename)
				return 0, err
			}
		}
	}
	fmt.Println("DONE after " + strconv.Itoa(cnt))
	writer.Close()
	conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
	if err != nil {
		fmt.Println(err)
		return 0, err
	}

	defer conn.Close()
	ch, err := conn.Channel()

	q, err := ch.QueueDeclare(
		w.Topic, // name
		false,   // durable
		false,   // delete when unused
		false,   // exclusive
		false,   // no-wait
		nil,     // arguments
	)

	if err != nil {
		fmt.Println(err)
		return 0, err
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	body := "Hello World!"
	err = ch.PublishWithContext(ctx,
		"",     // exchange
		q.Name, // routing key
		false,  // mandatory
		false,  // immediate
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        []byte(body),
		})

	if err != nil {
		return 0, err
	}

	log.Printf(" [x] Sent %s\n", body)

	return cnt, nil
}
