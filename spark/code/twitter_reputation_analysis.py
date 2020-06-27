# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import json
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.streaming import StreamingContext
import pyspark
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import pyspark.sql.types as tp
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, OneHotEncoderEstimator, VectorAssembler
from pyspark.ml.feature import StopWordsRemover, Word2Vec, RegexTokenizer
from pyspark.ml.classification import LogisticRegression
from pyspark.sql import Row
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.classification import NaiveBayes
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
import os
import re
print(os.path.realpath(__file__))

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

## is there a field in the mapping that should be used to specify the ES document ID
# "es.mapping.id": "id"
# Define Training Set Structure
tweetSchema = tp.StructType([
    # Todo use proper timestamp
    tp.StructField(name= 'tweet', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'timestamp', dataType= tp.LongType(),  nullable= True),
    tp.StructField(name= 'in_reply_to_status_id', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'in_reply_to_screen_name', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'user_id', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'user_screen_name', dataType= tp.StringType(),  nullable= True)
])


schema = tp.StructType([
    tp.StructField(name= 'id', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'subjective',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'positive',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'negative',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'ironic',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'lpositive',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'lnegative',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'top',       dataType= tp.IntegerType(),  nullable= True),
    tp.StructField(name= 'tweet',       dataType= tp.StringType(),   nullable= True)
])
sc = SparkContext(appName="Tweet")
spark = SparkSession(sc)

sc.setLogLevel("WARN")
# read the dataset  
training_set = spark.read.csv('../tap/spark/dataset/training_set_sentipolc16.csv',
                         schema=schema,
                         header=True,
                         sep=',')
training_set                        


# define stage 1: tokenize the tweet text    
stage_1 = RegexTokenizer(inputCol= 'tweet' , outputCol= 'tokens', pattern= '\\W')
# define stage 2: remove the stop words
stage_2 = StopWordsRemover(inputCol= 'tokens', outputCol= 'filtered_words')
# define stage 3: create a word vector of the size 100
stage_3 = Word2Vec(inputCol= 'filtered_words', outputCol= 'vector', vectorSize= 100)
# define stage 4: Logistic Regression Model
model = LogisticRegression(featuresCol= 'vector', labelCol= 'positive')
# setup the pipeline
pipeline = Pipeline(stages= [stage_1, stage_2, stage_3, model])

# fit the pipeline model with the training data
pipelineFit = pipeline.fit(training_set)

modelSummary=pipelineFit.stages[-1].summary
modelSummary.accuracy

def isAboutUser(json):
    return ("in_reply_to_screen_name" in json and json["in_reply_to_screen_name"] == twitter_user[0]) or ("in_reply_to_user_id" in json and json["in_reply_to_user_id"] == twitter_user[1])

#To strip URLS from tweets
def stripUrl(string):
    return re.sub(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}     /)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', '', string)

#Check whether a tweet is longer than 20 characters withouth urls
def filterShortTweets(json):
    return (len(stripUrl(json['full_text'])) > 20 if "full_text" in json else len(stripUrl(json['text'])) > 20)

def get_prediction_json(key,rdd):
    print("********************")
    tweet=rdd.map(lambda (key, value): json.loads(value))\
    .filter(lambda json_object : filterShortTweets(json_object))\
    .filter(lambda json_object: isAboutUser(json_object))\
    .map(
        lambda json_object: (
            (json_object["full_text"] if "full_text" in json_object else json_object["text"]),
            long(json_object['timestamp_ms']),
            json_object['in_reply_to_status_id'],
            (json_object['in_reply_to_screen_name'] if "in_reply_to_screen_name" in json_object else "Anonimo"),
            json_object['user']['id_str'],
            (json_object['user']['screen_name'] if "screen_name" in json_object['user'] else "Anonimo"),
        )
    )
    tweetstr=tweet.collect()
    if not tweetstr:
        print("No Tweet")
        return
    
    print("********************")
    print(tweetstr)
    # create a dataframe with column name 'tweet' and each row will contain the tweet
    rowRdd = tweet.map(lambda w: Row(tweet=w[0], timestamp=w[1], in_reply_to_status_id=w[2], in_reply_to_screen_name=w[3], user_id=w[4], user_screen_name=w[5]))
    # create a spark dataframe
    wordsDataFrame = spark.createDataFrame(rowRdd,schema=tweetSchema)
    wordsDataFrame.show(truncate=False)
    # transform the data using the pipeline and get the predicted sentiment
    pipelineFit.transform(wordsDataFrame).select('tweet','prediction').show()

brokers="10.0.100.23:9092"
topic = sys.argv[1]
twitter_user = sys.argv[2:]

ssc = StreamingContext(sc, 1)
kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers, "auto.offset.reset": "smallest"}) #auto.offset.reset needed to check older (or saved) kafka RDD

# get the predicted sentiments for the tweets received
kvs.foreachRDD(get_prediction_json)

#tweets.pprint()

ssc.start()
ssc.awaitTermination()