IDIR =./include
LDIR =./lib
LIBUSBIDIR = /usr/include/libusb-1.0
LIBUSBLDIR = /usr/lib/x86_64-linux-gnu
CC=gcc
CFLAGS = -std=c99 -fPIC 
SRCDIR = ./src
FILENAME = sc5506a

SLIB = libsc5506a.so

_DEPS = sc5506a.h 
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

all: obj shared static

obj:
	$(CC) -c -D _LINUX $(SRCDIR)/$(FILENAME).c $(CFLAGS) -I$(IDIR) -I$(LIBUSBIDIR) -o $(SRCDIR)/$(FILENAME).o
	
shared:
	$(CC) -shared -fpic  $(SRCDIR)/$(FILENAME).o -L$(LIBUSBLDIR) -lm -lusb-1.0 -o $(LDIR)/$(SLIB).1.0

static: 
	ar -cvq $(LDIR)/lib$(FILENAME).a $(SRCDIR)/$(FILENAME).o

install:
	sudo cp $(LDIR)/lib$(FILENAME).* /usr/lib
	sudo ln -sf /usr/lib/$(SLIB).1.0 /usr/lib/$(SLIB).1
	sudo ln -sf /usr/lib/$(SLIB).1.0 /usr/lib/$(SLIB)

uninstall: 
	sudo rm /usr/lib/$(SLIB)*

.PHONY: clean

clean:
	rm -f $(SRCDIR)/$(FILENAME).o $(LDIR)/*.*
