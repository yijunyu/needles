import os
import sys
import codecs
import numpy as np
import argparse
import time
import re
import math
from file_utils import *
from keras.optimizers import *
from sklearn.model_selection import KFold
from keras.models import Sequential
from data_utils import *
from neural_network import *
from keras.utils.np_utils import to_categorical
from sklearn.metrics import average_precision_score
from evaluation import *
import keras.preprocessing.text as text
import argparse
from argument_parser import *
from needles import save_bug_to_pb, save_code_to_pb, load_bug_from_pb, load_code_from_pb
from needles import save_bug_to_fbs, save_onehot_bug_to_fbs, save_code_to_fbs, load_bug_from_fbs, load_code_from_fbs
from needles import onehot_to_int, int_to_onehot, onehot_seq_to_int_seq
import time


def main():
    model_dir_path = "../model/model_tomcat"
    bug_contents_path = "../data/Tomcat/Tomcat_bug_content"
    code_contents_path = "../data/Tomcat/Tomcat_code_content"
    file_oracle_path = "../data/Tomcat/Tomcat_oracle"
    method_oracle_path = "../data/Tomcat/Tomcat_relevant_methods"
    prediction_dir_path = "../eval/Tomcat_predictions"
    evaluation_file_path = "../eval/Tomcat_eval"
    lstm_seq_length = 200
    vocabulary_size = 1500
    neg_method_num = 10
    split_ratio = 0.8
    
  #  os.mkdir(prediction_dir_path)
    [bug_contents,code_contents,file_oracle, method_oracle] = load_data(bug_contents_path, code_contents_path, file_oracle_path, method_oracle_path)

    tokenizer = get_tokenizer(bug_contents, code_contents, vocabulary_size)
    nb_train_bug = int(math.floor(len(bug_contents)* split_ratio))
    epoch = 29 
    model = load_model(os.path.join(model_dir_path, "model_structure"), os.path.join(model_dir_path, "weight_epoch_{}".format(epoch)))

    test_oracle, predictions = generate_predictions(model, bug_contents, code_contents, file_oracle, method_oracle, nb_train_bug, tokenizer, lstm_seq_length, vocabulary_size, neg_method_num)
    print (sys.argv[1], sys.argv[2], predictions)

    # export_predictions(test_oracle, predictions, prediction_dir_path)

    # evaluations = evaluate(predictions, test_oracle, 1, 0.65)
    # export_evaluation(evaluations, evaluation_file_path)

def generate_predictions(model, bug_contents, code_contents, file_oracle, method_oracle, nb_train_bug, tokenizer, lstm_seq_length, vocabulary_size, neg_method_num, embedding_dimension = -1):
    predictions = []
    test_oracle = []
    code_method_list = []
    for one_code_content in code_contents:
        method_list = get_top_methods_in_file(one_code_content, lstm_seq_length, neg_method_num, tokenizer)
        code_method_list.append(method_list)

    Initial = len(sys.argv) > 3
    if Initial:
	    #traverse each code file
	    id = 0
	    for method_list in code_method_list:
		# print("for one code:")
		#obtain the prediction score for each method
		vec = []
		for one_method in method_list:
		    one_hot_code_seq = convert_to_lstm_input_form([one_method], tokenizer,lstm_seq_length, vocabulary_size, embedding_dimension = embedding_dimension)
		    if len(one_hot_code_seq) == 0:
			continue
		    int_seq = onehot_seq_to_int_seq(one_hot_code_seq)
		    vec.append(int_seq)
		id  = id + 1
		save_code_to_fbs(id, vec)
	    #print("===saved the code vectors ===")
    else:
      one_bug_prediction = []
      for bug_index in range(nb_train_bug, len(bug_contents)):
	# skip for other processors
	if bug_index % 8 != int(sys.argv[1]):
		continue
        # print("generating predictions for bug {} :".format(bug_index))
	one_hot_bug_seq = convert_to_lstm_input_form([bug_contents[bug_index]], tokenizer,lstm_seq_length, vocabulary_size, embedding_dimension=embedding_dimension)
	if len(one_hot_bug_seq) == 0:
	    print("testing bug sequence is void!")
	    continue
	# save_bug_to_fbs(bug_index, onehot_seq_to_int_seq(one_hot_bug_seq))
        # bug_index = int(sys.argv[1])
        test_oracle.append(file_oracle[bug_index][0])
	# vec = load_bug_from_fbs(bug_index)
	#N = len(vec)
	#for i in range(N):
	#	v = []
	#	M = len(vec[i])
	#	for j in range(M):
	#		v.append(int_to_onehot(vec[i][j], vocabulary_size))
	#	one_hot_bug_seq.append(v)
	#	one_hot_bug_seq = np.asarray(one_hot_bug_seq)
	one_hot_bug_seq = np.asarray(one_hot_bug_seq)
    	#print("===loaded onehot bug vectors in the batch ===")
	start_time = time.time()
    	id = int(sys.argv[2])
	vec = load_code_from_fbs(id)
	L = len(vec)
	for k in range(L):
		scores = []
		one_hot_code_seq = []
		v = vec[k]
		N = len(v)
		for i in range(N):
			m = []
			M = len(v[i])
			for j in range(M):
				m.append(int_to_onehot(v[i][j], vocabulary_size))
			one_hot_code_seq.append(m)
		one_hot_code_seq = np.asarray(one_hot_code_seq)
		#print("===loaded onehot code vectors in the batch ===")
		prediction_result = model.predict([one_hot_bug_seq, reverse_seq(one_hot_bug_seq), one_hot_code_seq, reverse_seq(one_hot_code_seq)]);
		value = abs(prediction_result[0][0][0])
		scores.append(value)
		#Here we can define different strategies from the method scores to the file score, here we only consider the average as a start
	end_time = time.time()
	# print end_time - start_time
	one_bug_prediction.append(np.mean(scores))
	# print("score for this code file: {}".format(np.mean(scores)))
      predictions.append(one_bug_prediction)
    return test_oracle, predictions

if __name__ == '__main__':
    main()
