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

    return
    export_predictions(test_oracle, predictions, prediction_dir_path)

    evaluations = evaluate(predictions, test_oracle, 10, 0.65)
    export_evaluation(evaluations, evaluation_file_path)

def generate_predictions(model, bug_contents, code_contents, file_oracle, method_oracle, nb_train_bug, tokenizer, lstm_seq_length, vocabulary_size, neg_method_num, embedding_dimension = -1):
    predictions = []
    test_oracle = []
    code_method_list = []
    for one_code_content in code_contents:
        method_list = get_top_methods_in_file(one_code_content, lstm_seq_length, neg_method_num, tokenizer)
        code_method_list.append(method_list)

    for bug_index in range(nb_train_bug, len(bug_contents)):
        # print("generating predictions for bug {} :".format(bug_index))

        one_bug_prediction = []
        one_hot_bug_seq = convert_to_lstm_input_form([bug_contents[bug_index]], tokenizer,lstm_seq_length, vocabulary_size, embedding_dimension=embedding_dimension)
        if len(one_hot_bug_seq) == 0:
            print("testing bug sequence is void!")
            continue
	print (one_hot_bug_seq[0])
    	return test_oracle, predictions
        test_oracle.append(file_oracle[bug_index][0])
        one_hot_bug_seq = np.asarray(one_hot_bug_seq)
        #traverse each code file
        for method_list in code_method_list:
            # print("for one code:")
            #obtain the prediction score for each method
            scores = []
            #for one_method in method_list:
	    if True:
            	one_method = method_list[0]
                one_hot_code_seq = convert_to_lstm_input_form([one_method], tokenizer,lstm_seq_length, vocabulary_size, embedding_dimension = embedding_dimension)
                if len(one_hot_code_seq) == 0:
                    continue
                one_hot_code_seq = np.asarray(one_hot_code_seq)
		continue
                prediction_result = model.predict([one_hot_bug_seq, reverse_seq(one_hot_bug_seq), one_hot_code_seq, reverse_seq(one_hot_code_seq)]);
                value = abs(prediction_result[0][0][0])
                # print("prediction_result: {}".format(value))
                scores.append(value)


            #Here we can define different strategies from the method scores to the file score, here we only consider the average as a start
            one_bug_prediction.append(np.mean(scores))
            # print("score for this code file: {}".format(np.mean(scores)))
        predictions.append(one_bug_prediction)
    return test_oracle, predictions


if __name__ == '__main__':
    main()
