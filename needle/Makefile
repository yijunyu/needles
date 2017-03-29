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

#target+=needle_generated.h
#target+=needle.pb.h needle.pb.cc
target+=Code.py Kind.py Seq.py Sequences.py
target+=needle_pb2.py needle.fbs
target+=bug/1.pb
target+=bug/1.fbs
target+=code/1.pb
target+=code/1.fbs

all: $(target)

bug/1.pb bug/1.fbs code/1.pb code/1.fbs: needle.py
	$(gtime) -f%e python needle.py $@
	$(gtime) -f%e python needle.py load $@

ifeq ($(UNAME_S),Linux)
needle.cc: needle.pb.h needle.pb.cc
needle.cc: needle_generated.h
needle_pb: needle.cc
	$(CXX) $(OPT) -DPB_needle -I/usr/local/include -Irapidxml $^ /usr/local/lib/libprotobuf.a -o $@

needle_fbs: needle.cc
	$(CXX) $(OPT) -std=c++11 -DFBS_needle -I/usr/local/include -Irapidxml $(FBS_LIB) $^ -o $@

install: needle_pb needle_fbs
	cp needle_pb /usr/local/bin/
	cp needle_fbs /usr/local/bin/
	cp needle.sh /usr/local/bin/needle
endif

ifeq ($(UNAME_S),Darwin)
needle: needle.cc
	$(CXX) $(OPT) -std=c++11 -DPB_needle -DFBS_needle -I/usr/local/include -Irapidxml $(PB_LIB) $(FBS_LIB) $^ -o $@

needle-debug: needle.cc
	$(CXX) $(OPT_DEBUG) -std=c++11 -DPB_needle -DFBS_needle -I/usr/local/include -Irapidxml $(PB_LIB) $(FBS_LIB) $^ -o $@

install: needle
	cp needle /usr/local/bin/

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

__main__.py: ./protobuf-3.2.0/src/protoc needle_pb2.py

needle_pb2.py: ./protobuf-3.2.0/src/protoc needle.proto
	protoc -I=. --python_out=. needle.proto

needle.pb.h needle.pb.cc: needle.proto
	protoc -I=. --cpp_out=. needle.proto

needle.fbs: needle.proto
	flatc --proto needle.proto

Code.py: needle.fbs
	flatc -p -o . needle.fbs
	mv _needle/Code.py .
	mv _needle/Sequences.py .
	mv _needle/_Sequences/Seq.py .
	mv _needle/_Sequences/Kind.py .

needle_generated.h: needle.fbs
	flatc --cpp -o . needle.fbs

%: %.in
	cpp -E -P $*.in | grep -v "^[ ]*$$" | grep -v "^0$$" > $@

clean:
	rm -rf $(target) test/*.fbs test/*.pb test/*.xml _needle
