from __future__ import print_function

import sys
import json
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

def getMessage(json_object):
    try:
        return (json_object["user"]["screen_name"], json_object["full_text"])
    except:
        return (json_object["user"]["screen_name"], json_object["text"])

sc = SparkContext(appName="PythonStreamingTwitter")

sc.setLogLevel("WARN")
ssc = StreamingContext(sc, 1)

brokers="10.0.100.23:9092"
topic = sys.argv[1]

kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
kvs.pprint()

tweets = kvs.map(lambda value: json.loads(value[1]))\
            .map(lambda json_object: getMessage(json_object))


tweets.pprint()

ssc.start()
ssc.awaitTermination()
