IDIR =../include
LDIR = /usr/include
LIBUSBIDIR = /usr/include/libusb-1.0
LIBUSBLDIR = /usr/lib/x86_64-linux-gnu
CC=gcc
CFLAGS = -std=c99 -fPIC 
FILENAME = example

SLIB = libsc5413a.so

_DEPS = sc5413a.h 
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

all: obj example static

obj:
	$(CC) -c -D _LINUX $(FILENAME).c $(CFLAGS) -I$(IDIR) -I$(LIBUSBIDIR) -o example.o
	
example:
	$(CC) $(FILENAME).o -lsc5413a -lusb-1.0 -L$(LDIR) -L$(LIBUSBLDIR) -o sc5413a_example

static:	
	$(CC) $(FILENAME).o ../lib/libsc5413a.a -lusb-1.0 -lm -L$(LDIR)-L$(LIBUSBLDIR) -o sc5413a_example_static

.PHONY: clean

clean:
	rm -f $(FILENAME).o sc5413a_example*
