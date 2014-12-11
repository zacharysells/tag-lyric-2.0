all: format_mp3

format_mp3: format_mp3.o
	g++ format_mp3.o -o format_mp3
	
format_mp3.o: format_mp3.cpp
	g++ -c format_mp3.cpp
	
clean:
	rm -rf format_mp3.o format_mp3

install: format_mp3
	cp format_mp3 /usr/local/bin/taglyric_files/
	cp taglyric2.0 /usr/local/bin/
