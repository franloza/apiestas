import json
import os

from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

from api.app.models.matches import MatchInDB
from .finder import SureBetsFinder


def main():
    consumer = AvroConsumer(
        {'group.id': os.environ['APIESTAS_DBNAME'],
         'bootstrap.servers': os.environ['KAFKA_BROKER_URL'],
         'schema.registry.url': os.environ['KAFKA_REST_SCHEMA_REGISTRY_URL']
         })
    consumer.subscribe([os.environ['KAFKA_SUBSCRIPTION_NAME']])
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

        # Find surebets
        doc = json.loads(msg.value())
        match = MatchInDB(**doc)
        surebets = SureBetsFinder(match.bets).find_all()
        # TODO: Post surebets to API

    consumer.close()


if __name__ == '__main__':
    main()

