import json

from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

from .calculator import process_bets

consumer = AvroConsumer({'group.id': 'apiestas','bootstrap.servers': 'localhost:9092', 'schema.registry.url': 'http://127.0.0.1:8081'})
consumer.subscribe(['mongo.apiestas.matches'])
while True:
    try:
        msg = consumer.poll(10)

    except SerializerError as e:
        print("Message deserialization failed for {}: {}".format(msg, e))
        break

    if msg is None:
        continue

    if msg.error():
        print("AvroConsumer error: {}".format(msg.error()))
        continue

    doc = json.loads(msg.value())
    process_bets(doc["bets"])


consumer.close()
