## IMPORTS


from __future__ import print_function
import json
from pyspark import SparkContext
from pyspark.sql.session import SparkSession
from pyspark.streaming import StreamingContext
import pyspark
from pyspark.conf import SparkConf
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
import re
import os
import sys
import nltk







## FUNCTIONS

#Parse the input from the command line to get users' usernames and IDs
def parseUser(twitter_user_lists):
    return [item for sublist in twitter_user_lists for item in sublist]

#Check whether the tweet is about the user we gave as input
def isAboutUser(json):
    return ("in_reply_to_screen_name" in json and json["in_reply_to_screen_name"] in twitter_user) or ("in_reply_to_user_id" in json and json["in_reply_to_user_id"] in twitter_user)

#To strip URLS from tweets
def stripUrl(string):
    return re.sub(r'https?:\/\/.*[\r\n]*', '', string)

#To strip Nicknames from tweets
def stripNicknames(string):
    return re.sub(r'(@[a-zA-Z0-9]+)+', '', string)

#Clean tweet's text using strip functions
def cleanTweet(raw):
    cleaning = stripUrl(raw)
    clean = stripNicknames(cleaning)
    return clean

#Check whether a tweet is longer than 20 characters withouth urls (usually a meeningful tweet is long about 26 characters)
def filterShortTweets(json):
    return (len(stripUrl(json['full_text'])) > 20 if "full_text" in json else len(cleanTweet(json['text'])) > 20)


#Check whether the language of the tweet is processable
def filterLanguage(json):
    if "lang" not in json or json["lang"] not in ["en","it"]:
        return False
    return True

# Gets the predicted sentiments for the tweets received
def get_prediction(key,rdd):
    print("********************")
    tweet=rdd.map(lambda value: json.loads(value[1]))\
    .filter(lambda json_object : filterShortTweets(json_object))\
    .filter(lambda json_object: isAboutUser(json_object))\
    .map(
        lambda json_object: (
            (json_object["full_text"] if "full_text" in json_object else json_object["text"]),
            int(json_object['timestamp_ms']),
            json_object['in_reply_to_status_id'],
            (json_object['in_reply_to_screen_name'] if "in_reply_to_screen_name" in json_object else "Anonimo"),
            json_object['user']['id_str'],
            (json_object['user']['screen_name'] if "screen_name" in json_object['user'] else "Anonimo"),
            (json_object['lang'] if "lang" in json_object else "en"),
        )
    )
    tweetstr=tweet.collect()
    if not tweetstr:
        print("No Tweet")
        return
    
    print("********************")
    print(tweetstr)
    # create a dataframe with column name 'tweet' and each row will contain the tweet
    rowRdd = tweet.map(lambda w: Row(tweet=w[0], timestamp=w[1], in_reply_to_status_id=w[2], in_reply_to_screen_name=w[3], user_id=w[4], user_screen_name=w[5], language=w[6]))
    # create a spark dataframe
    wordsDataFrame = spark.createDataFrame(rowRdd,schema=tweetSchema)
    wordsDataFrame.show(truncate=False)
    # transform the data using the pipeline and get the predicted sentiment
    data=pipelineFit.transform(wordsDataFrame)
    data.show()
    new = data.rdd.map(lambda item: {
        'timestamp': item['timestamp'],
        'tweet': item['tweet'],
        'in_reply_to_status_id': item['in_reply_to_status_id'],
        'in_reply_to_screen_name': item['in_reply_to_screen_name'],
        'user_id':  item['user_id'],
        'user_screen_name': item['user_screen_name'],
        'language' : item['language'],
        'sentiment': (item['prediction'] if item['language'] == "it" else (1.0 if sid.polarity_scores(item[0])['compound'] >= 0 else 0.0) )
    })
    final_rdd = new.map(json.dumps).map(lambda x: ('key', x))
    print(final_rdd.collect())
    final_rdd.saveAsNewAPIHadoopFile(
    path='-',
    outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
    keyClass="org.apache.hadoop.io.NullWritable",
    valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
    conf=es_write_conf)




## INITIALIZATIONS VARIABLES AND ELEMENTS

nltk.download('vader_lexicon')

brokers="10.0.100.23:9092"
topic = sys.argv[1]
twitter_user = parseUser(list(map(lambda x: x.split(","), sys.argv[2:])))
elastic_host="10.0.100.51"
elastic_index="twitter"
elastic_document="_doc"

es_write_conf = {
"es.nodes" : elastic_host,
"es.port" : '9200',
"es.resource" : '%s/%s' % (elastic_index,elastic_document),
"es.input.json" : "yes"
}






## SPARK/ES ELEMENTS DEFINITIONS

# Define Training Set Structure
tweetSchema = tp.StructType([
    # Todo use proper timestamp
    tp.StructField(name= 'tweet', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'timestamp', dataType= tp.LongType(),  nullable= True),
    tp.StructField(name= 'in_reply_to_status_id', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'in_reply_to_screen_name', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'user_id', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'user_screen_name', dataType= tp.StringType(),  nullable= True),
    tp.StructField(name= 'language', dataType= tp.StringType(),  nullable= True)
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

# Create Spark Context
sc = SparkContext(appName="Tweet")
spark = SparkSession(sc)

sc.setLogLevel("WARN")

# Elastic Search
conf = SparkConf(loadDefaults=False)
conf.set("es.index.auto.create", "true")








## SPARK ML PIPELINE


# read the dataset  
training_set = spark.read.csv('../tap/spark/dataset/training_set_sentipolc16.csv',
                         schema=schema,
                         header=True,
                         sep=',')

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

ssc = StreamingContext(sc, 1)
kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers, "auto.offset.reset": "smallest"})







## PREDICTION SECTION

from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()
kvs.foreachRDD(get_prediction)

mapping = {
    "mappings": {
        "properties": {
            "timestamp": {
                "type": "date"
            }
        }
    }
}






## DELIVERY TO ES

from elasticsearch import Elasticsearch
elastic = Elasticsearch(hosts=[elastic_host])

# make an API call to the Elasticsearch cluster
# and have it return a response:
response = elastic.indices.create(
    index=elastic_index,
    body=mapping,
    ignore=400 # ignore 400 already exists code
)

if 'acknowledged' in response:
    if response['acknowledged'] == True:
        print ("INDEX MAPPING SUCCESS FOR INDEX:", response['index'])

    # catch API error response
    elif 'error' in response:
        print ("ERROR:", response['error']['root_cause'])
        print ("TYPE:", response['error']['type'])

ssc.start()
ssc.awaitTermination()
