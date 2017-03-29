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
import _needles
from Code import *
from Seq import *
from Sequences import *
from Kind import *
###################################################
## create a random record and save it into protobuf
###################################################
def prepare_seq_as_pb(seq, id, kind):
    r = np.random.random_sample([200,1500])
    seq.id= id
    for i in range(1, 200):
        vi = seq.seq.add()
        for j in range(1, 1500):
            vi.vec.append(r[i][j])
    seq.kind = kind # 0 = BUG, 1 = METHOD 
    return

######################################################
## create a random record and save it into flatbuffers
######################################################
def prepare_seq_as_fbs(builder, id, kind):
    r = np.random.random_sample([200,1500])
    sequences=[]
    for i in range(1,200):
        vec = SeqStartVecVector(builder, 1500)
        for j in range(1, 1500):
            builder.PrependFloat64(r[i][j])
        builder.EndVector(1500)
        SeqStart(builder)
        seq = SeqEnd(builder)
        sequences.append(seq)
    N = len(sequences)
    SequencesStartSeqVector(builder, N)
    for i in reversed(range(1, N)):
        builder.PrependUOffsetTRelative(sequences[i])
    sequence = builder.EndVector(N)
    SequencesStart(builder) # Bug
    SequencesAddKind(builder, 0) # Bug
    SequencesAddId(builder, id) # ID
    SequencesAddSeq(builder, sequence)
    return SequencesEnd(builder)

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
    ext = sys.argv[1].rsplit("/")[1].split(".")[1]
    is_bug = sys.argv[1].startswith("bug/")
    is_code = sys.argv[1].startswith("code/")
    if is_saving: # saving
        if is_bug:
            if ext == "pb":
                # store the record into the bug identified by the ID in filename: bug/ID.pb
                bug = SEQ()
                prepare_seq_as_pb(bug, int(sys.argv[1].rsplit("/")[1].split(".")[0]), 0)
                serializedMessage = bug.SerializeToString()
                out = open(sys.argv[1], 'wb')
                out.write(serializedMessage)
                out.close()
            if ext == "fbs":
                builder = flatbuffers.Builder(0)
                bug = prepare_seq_as_fbs(builder, int(sys.argv[1].rsplit("/")[1].split(".")[0]), 0)
                builder.Finish(bug)
                gen_buf, gen_off = builder.Bytes, builder.Head()
                out = open(sys.argv[1], 'wb')
                out.write(gen_buf[gen_off:])
                out.close()
        if is_code:
            if ext == "pb":
                code = CODE()
                code.id=int(sys.argv[1].rsplit("/")[1].split(".")[0])
                for k in range(1,10):
                    method = code.method.add() # SEQ
                    prepare_seq_as_pb(method, k, 1)
                serializedMessage = code.SerializeToString()
                out = open(sys.argv[1], 'wb')
                out.write(serializedMessage)
                out.close()
            if ext == "fbs":
                builder = flatbuffers.Builder(0)
                methods=[]
                for k in range(1,10):
                    methods.append(prepare_seq_as_fbs(builder, k, 1))
                N = len(methods)
                CodeStartMethodVector(builder, N)
                for k in reversed(range(1,N)):
                    builder.PrependUOffsetTRelative(methods[k])
                method = builder.EndVector(N)
                CodeStart(builder)
                CodeAddId(builder, int(sys.argv[1].rsplit("/")[1].split(".")[0]))
                CodeAddMethod(builder, method)
                code = CodeEnd(builder)
                builder.Finish(code)
                gen_buf, gen_off = builder.Bytes, builder.Head()
                out = open(sys.argv[1], 'wb')
                out.write(gen_buf[gen_off:])
                out.close()
    else: ## loading
        if is_bug:
            if ext == "pb":
                bug = SEQ()
                with open(sys.argv[1], 'rb') as f:
                   bug.ParseFromString(f.read())
                   f.close()
                   # print pb2json(bug)
            if ext == "fbs":
                with open(sys.argv[1], 'rb') as f:
                   buf = f.read()
                   buf = bytearray(buf)
                   f.close()
                   data = Sequences.GetRootAsSequences(buf, 0)
        if is_code:
            if ext == "pb":
                code = CODE()
                with open(sys.argv[1], 'rb') as f:
                   code.ParseFromString(f.read())
                   f.close()
                   #print pb2json(code)
            if ext == "fbs":
                with open(sys.argv[1], 'rb') as f:
                   buf = f.read()
                   buf = bytearray(buf)
                   f.close()
                   data = Code.GetRootAsCode(buf, 0)
if __name__ == "__main__":
    main()
