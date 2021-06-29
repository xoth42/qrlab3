IDIR =../include
LDIR = /usr/include
LIBUSBIDIR = /usr/include/libusb-1.0
LIBUSBLDIR = /usr/lib/x86_64-linux-gnu
CC=gcc
CFLAGS = -std=c99 -fPIC 
FILENAME = example

SLIB = libsc5506a.so

_DEPS = sc5506a.h 
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

all: obj example static

obj:
	$(CC) -c -D _LINUX $(FILENAME).c $(CFLAGS) -I$(IDIR) -I$(LIBUSBIDIR) -o example.o
	
example:
	$(CC) $(FILENAME).o -lsc5506a -lusb-1.0 -L$(LDIR) -L$(LIBUSBLDIR) -o sc5506a_example

static:	
	$(CC) $(FILENAME).o ../lib/libsc5506a.a -lusb-1.0 -lm -L$(LDIR)-L$(LIBUSBLDIR) -o sc5506a_example_static

.PHONY: clean

clean:
	rm -f $(FILENAME).o sc5506a_example*
