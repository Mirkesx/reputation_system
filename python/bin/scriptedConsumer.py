# https://towardsdatascience.com/kafka-python-explained-in-10-lines-of-code-800e3e07dad
from kafka import KafkaConsumer
from json import loads
import sys

consumer = KafkaConsumer(
     sys.argv[1],
     bootstrap_servers=['kafkaServer:9092'],
     auto_offset_reset='latest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))

def getText(mess):
    try:
        return mess["full_text"]
    except:
        return mess["text"]

for message in consumer:
    message = getText(message.value)
    print('{}\n\n\n'.format(message))