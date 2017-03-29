UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	gtime=/usr/bin/time
	CXX=g++
endif
ifeq ($(UNAME_S),Darwin)
	gtime=gtime
	CXX=c++
endif

OPT_DEBUG=-g
OPT=-O3

FBS_LIB=-L/usr/local/lib -lflatbuffers
PB_LIB=$(shell pkg-config --libs protobuf)

#target+=needles_generated.h
#target+=needles.pb.h needles.pb.cc
target+=Code.py Kind.py Seq.py Sequences.py
target+=needles_pb2.py needles.fbs
target+=bug/1.pb
target+=bug/1.fbs
target+=code/1.pb
target+=code/1.fbs

all: $(target)

bug/1.pb bug/1.fbs code/1.pb code/1.fbs: needles.py
	$(gtime) -f%e python needles.py $@
	$(gtime) -f%e python needles.py load $@

ifeq ($(UNAME_S),Linux)
needles.cc: needles.pb.h needles.pb.cc
needles.cc: needles_generated.h
needles_pb: needles.cc
	$(CXX) $(OPT) -DPB_needles -I/usr/local/include -Irapidxml $^ /usr/local/lib/libprotobuf.a -o $@

needles_fbs: needles.cc
	$(CXX) $(OPT) -std=c++11 -DFBS_needles -I/usr/local/include -Irapidxml $(FBS_LIB) $^ -o $@

install: needles_pb needles_fbs
	cp needles_pb /usr/local/bin/
	cp needles_fbs /usr/local/bin/
	cp needles.sh /usr/local/bin/needles
endif

ifeq ($(UNAME_S),Darwin)
needles: needles.cc
	$(CXX) $(OPT) -std=c++11 -DPB_needles -DFBS_needles -I/usr/local/include -Irapidxml $(PB_LIB) $(FBS_LIB) $^ -o $@

needles-debug: needles.cc
	$(CXX) $(OPT_DEBUG) -std=c++11 -DPB_needles -DFBS_needles -I/usr/local/include -Irapidxml $(PB_LIB) $(FBS_LIB) $^ -o $@

install: needles
	cp needles /usr/local/bin/

endif

./protobuf-3.2.0/src/protoc: protobuf-3.2.0
	cd protobuf-3.2.0 && ./configure CXXFLAGS=-std=c++11 && make && sudo make install

protobuf-3.2.0:
	wget https://github.com/google/protobuf/releases/download/v3.2.0/protobuf-cpp-3.2.0.tar.gz
	tar xvfz protobuf-cpp-3.2.0.tar.gz

./googletest/googlemock/gtest/libgtest.a: googletest
	cd googletest
	cmake .
	make CXXFLAGS=-std=c++11
	sudo make install

./googletest/googlemock/libgmock.a: ./googletest/googlemock/gtest/libgtest.a
	cd googletest/googlemock
	cmake .
	make CXXFLAGS=-std=c++11
	sudo make install

srcML-src.tar.gz: 
	wget http://131.123.42.38/lmcrs/beta/srcML-src.tar.gz

srcML-src: srcML-src.tar.gz
	tar xvfz $^

./srcML-src/build/bin/srcml: srcML-src/
	cd srcML-src
	cmake .
	make
	sudo make install

%.json: __main__.py %.pb
	python $^ $@

%.pb: __main__.py %.xml
	python $^ $@

%.pb.xml: __main__.py %.pb
	python $^ $@

%.pb.cc: __main__.py %.pb
	python $^ $@

%.xml: %.cc
	srcml $^ -o $@

__main__.py: ./protobuf-3.2.0/src/protoc needles_pb2.py

needles_pb2.py: ./protobuf-3.2.0/src/protoc needles.proto
	protoc -I=. --python_out=. needles.proto

needles.pb.h needles.pb.cc: needles.proto
	protoc -I=. --cpp_out=. needles.proto

needles.fbs: needles.proto
	flatc --proto needles.proto

Code.py: needles.fbs
	flatc -p -o . needles.fbs
	mv _needles/Code.py .
	mv _needles/Sequences.py .
	mv _needles/_Sequences/Seq.py .
	mv _needles/_Sequences/Kind.py .

needles_generated.h: needles.fbs
	flatc --cpp -o . needles.fbs

%: %.in
	cpp -E -P $*.in | grep -v "^[ ]*$$" | grep -v "^0$$" > $@

clean:
	rm -rf $(target) test/*.fbs test/*.pb test/*.xml _needles
