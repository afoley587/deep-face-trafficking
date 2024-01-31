package connections

type Connection interface {
	Connect() error
	Read() error
	Write() error
	Close() error
}
