package writers

import (
	"context"
	"log"
	"strconv"
	"time"

	amqp "github.com/rabbitmq/amqp091-go"
	"gocv.io/x/gocv"
)

type PikaWriter struct {
	Topic    string
	Exchange string
}

func (w PikaWriter) Write(imgs <-chan gocv.Mat, size int) (int, error) {

	img := <-imgs // first frame

	if img.Empty() {
		return 0, nil
	}

	fchan := make(chan string)
	done := make(chan WriterGoroutineResult)
	batchPref := "/tmp/" + w.Topic
	go batchToFile(fchan, done, imgs, batchPref, size, img.Cols(), img.Rows())

	conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
	if err != nil {
		log.Println(err)
		return 0, err
	}

	defer conn.Close()
	ch, err := conn.Channel()

	err = ch.ExchangeDeclare(
		w.Exchange, // name
		"topic",    // type
		true,       // durable
		false,      // auto-deleted
		false,      // internal
		false,      // no-wait
		nil,        // arguments
	)

	if err != nil {
		log.Println(err)
		return 0, err
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	go func() {
		for fname := range fchan {
			log.Println("File " + fname + " finished")
			log.Println("Sending to Rabbit")
			err = ch.PublishWithContext(ctx,
				w.Exchange, // exchange
				w.Topic,    // routing key
				false,      // mandatory
				false,      // immediate
				amqp.Publishing{
					ContentType: "text/plain",
					Body:        []byte(fname),
				})

			// if err != nil {
			// 	return err
			// }

			log.Println(" [x] Sent " + fname)
		}
	}()

	res := <-done
	close(fchan)
	close(done)
	log.Println("DONE after " + strconv.Itoa(res.Count))
	return res.Count, res.Error
}
