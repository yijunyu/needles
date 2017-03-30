######################################################################
### Author: Yijun Yu
### demonstrating how to load/save protobuf and flatbuffers in Python
######################################################################
import os
import sys
import codecs
import numpy as np
import argparse
import time
import re
import math
import string

import flatbuffers
from pbjson import pb2json
#########  Importing generated code #########
# Protobuf
from needles_pb2 import Sequences as SEQ
from needles_pb2 import Code as CODE
# Flatbuffers
from Code import *
from Seq import *
from Sequences import *
from Kind import *
###################################################
## create a random record and save it into protobuf
###################################################
def prepare_seq_as_pb(seq, id, kind, r):
    seq.id= id
    for i in range(len(r)):
        vi = seq.seq.add()
        for j in range(len(r[i])):
            vi.vec.append(r[i][j])
    seq.kind = kind # 0 = BUG, 1 = METHOD 
    return

######################################################
## create a random record and save it into flatbuffers
######################################################
def prepare_seq_as_fbs(builder, id, kind, r):
    sequences=[]
    N = len(r)
    for i in range(N):
	M = len(r[i])
        SeqStartVecVector(builder, M)
        for j in range(M):
            builder.PrependFloat32(r[i][j])
        vec = builder.EndVector(M)
        SeqStart(builder)
	SeqAddVec(builder, vec)
        seq = SeqEnd(builder)
        sequences.append(seq)
    SequencesStartSeqVector(builder, N)
    for i in reversed(range(N)):
        builder.PrependUOffsetTRelative(sequences[i])
    sequence = builder.EndVector(N)
    SequencesStart(builder) # Bug
    SequencesAddKind(builder, 0) # Bug
    SequencesAddId(builder, id) # ID
    SequencesAddSeq(builder, sequence)
    return SequencesEnd(builder)

def load_bug_from_pb(id):
	with open("bug/" + str(id) + ".pb", 'rb') as f:
           bug = SEQ()
	   bug.ParseFromString(f.read())
           f.close()
	b = []
	for seq in bug.seq:
	   vec = []
	   for v in seq.vec:
		vec.append(v)	
	   b.append(vec)
	return b	

def load_code_from_pb(id):
	code = CODE()
	with open("code/" + str(id) + ".pb", 'rb') as f:
	   code.ParseFromString(f.read())
	   f.close()
	c = []
	for method in code.method:
		m = []
		for seq in method.seq:
			v = []
			for vec in seq.vec:
				v.append(vec)
			m.append(v)
		c.append(m)
	return c

def load_bug_from_fbs(id):
	with open("bug/" + str(id) + ".fbs", 'rb') as f:
	   buf = f.read()
	   buf = bytearray(buf)
	   f.close()
	   bug = Sequences.GetRootAsSequences(buf, 0)
	b = []
	N = bug.SeqLength()
	for j in range(N):
	   seq = bug.Seq(j)
	   vec = []
	   for i in reversed(range(seq.VecLength())):
		vec.append(seq.Vec(i))
	   b.append(vec)
	return b

def load_code_from_fbs(id):
	with open("code/" + str(id) + ".fbs", 'rb') as f:
	   buf = f.read()
	   buf = bytearray(buf)
	   f.close()
	   code = Code.GetRootAsCode(buf, 0)
	c = []
	for k in range(code.MethodLength()):
		m = []
           	method = code.Method(k)
		for j in range(method.SeqLength()):
		   seq = method.Seq(j)
		   vec = []
		   for i in reversed(range(seq.VecLength())):
			vec.append(seq.Vec(i))
		   m.append(vec)
		c.append(m)
	return c

def save_bug_to_pb(id, r):
	# store the record into the bug identified by the ID in filename: bug/ID.pb
	bug = SEQ()
	prepare_seq_as_pb(bug, id, 0, r)
	serializedMessage = bug.SerializeToString()
	out = open(sys.argv[1], 'wb')
	out.write(serializedMessage)
	out.close()

def save_bug_to_fbs(id, r):
	builder = flatbuffers.Builder(0)
	bug = prepare_seq_as_fbs(builder, id, 0, r)
	builder.Finish(bug)
	gen_buf, gen_off = builder.Bytes, builder.Head()
	out = open(sys.argv[1], 'wb')
	out.write(gen_buf[gen_off:])
	out.close()

def save_code_to_pb(id, c):
	code = CODE()
	code.id=id
	for k in range(len(c)):
	    method = code.method.add() # SEQ
	    r = c[k]
	    prepare_seq_as_pb(method, k, 1, r)
	serializedMessage = code.SerializeToString()
	out = open(sys.argv[1], 'wb')
	out.write(serializedMessage)
	out.close()

def save_code_to_fbs(id, c):
	builder = flatbuffers.Builder(0)
	methods=[]
	for k in range(len(c)):
	    r = c[k]
	    methods.append(prepare_seq_as_fbs(builder, k, 1, r))
	N = len(methods)
	CodeStartMethodVector(builder, N)
	for k in reversed(range(N)):
	    builder.PrependUOffsetTRelative(methods[k])
	method = builder.EndVector(N)
	CodeStart(builder)
	CodeAddId(builder, id)
	CodeAddMethod(builder, method)
	code = CodeEnd(builder)
	builder.Finish(code)
	gen_buf, gen_off = builder.Bytes, builder.Head()
	out = open(sys.argv[1], 'wb')
	out.write(gen_buf[gen_off:])
	out.close()

############################################################
## Main procedure:
##
##     python needles.py [(load|save)] (bug|code)/id.(pb|fbs)
##
## Options:
##     load or save
##     is_bug or is_code
##     pb = protobuf or fbs = flatbuffers
############################################################
def main():
    is_saving = True
    if sys.argv[1] == "save":
        sys.argv = sys.argv[1:] # shift
    if sys.argv[1] == "load":
        sys.argv = sys.argv[1:] # shift
        is_saving = False
    is_bug = sys.argv[1].startswith("bug/")
    is_code = sys.argv[1].startswith("code/")
    ext = sys.argv[1].rsplit("/")[1].split(".")[1]
    id=int(sys.argv[1].rsplit("/")[1].split(".")[0])
    if is_saving: # saving
        if is_bug:
            if ext == "pb":
		save_bug_to_pb(id, [[1,2],[1,2],[1,2]])
            if ext == "fbs":
		save_bug_to_fbs(id, [[1,2],[1,2],[1,2]])
        if is_code:
            if ext == "pb":
		save_code_to_pb(id, [[[1,2],[1,2],[1,2]],[[3],[4]]])
            if ext == "fbs":
		save_code_to_fbs(id, [[[1,2],[1,2],[1,2]],[[3],[4]]])
    else: ## loading
        if is_bug:
            if ext == "pb":
		bug = load_bug_from_pb(id)
		print bug
            if ext == "fbs":
		bug = load_bug_from_fbs(id)
		print bug
        if is_code:
            if ext == "pb":
		code = load_code_from_pb(id)
		print code
            if ext == "fbs":
		code = load_code_from_fbs(id)
		print code
if __name__ == "__main__":
    main()
