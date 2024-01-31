package connections

import amqp "github.com/rabbitmq/amqp091-go"

type AmpqConnection struct {
	Connection *amqp.Connection
}

func (c AmpqConnection) Connect() error {
	return nil
}

func (c AmpqConnection) Read() error {
	return nil
}

func (c AmpqConnection) Write() error {
	return nil
}

func (c AmpqConnection) Close() error {
	return nil
}
