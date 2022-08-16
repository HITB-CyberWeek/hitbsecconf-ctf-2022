	

TARGET = 8
OBJ = $(TARGET).o
SRC = $(TARGET).cpp
CC = gcc
CFLAGS = -g
LDFLAGS = -nostdlib -nostartfiles -static
GLIBCDIR = /home/task/glibc_build/lib
INCDIR = /home/task/glibc_build/include
STARTFILES = $(GLIBCDIR)/crt1.o $(GLIBCDIR)/crti.o `gcc --print-file-name=crtbegin.o`
ENDFILES = `gcc --print-file-name=crtend.o` $(GLIBCDIR)/crtn.o
LIBGROUP = -Wl,--start-group $(GLIBCDIR)/libc.a -lgcc -lgcc_eh -Wl,--end-group

$(TARGET): $(OBJ)
	$(CC) $(LDFLAGS) -o $@ $(STARTFILES) $^ $(LIBGROUP) $(ENDFILES) 

$(OBJ): $(SRC)
	$(CC) $(CFLAGS) -c $^ -I `gcc --print-file-name=include` -I $(INCDIR)

clean:
	rm -f *.o *.~ $(TARGET)
	rm test.c.*
	rm a.out
