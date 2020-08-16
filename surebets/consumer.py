import json
from datetime import datetime, timedelta
import requests

from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from loguru import logger
from pydantic import ValidationError

from api.app.models.matches import MatchInDB
from .finder import SureBetsFinder
from .helpers import parse_mongo_dates


def run_consumer(group_id : str, broker_url: str, registry_url: str, subscription_name: str, apiestas_url: str):
    logger.info(f"Kafka consumer listening to {broker_url} and subscribed to {subscription_name}")
    consumer = AvroConsumer(
        {'group.id': group_id,
         'bootstrap.servers': broker_url,
         'schema.registry.url': registry_url
         })
    consumer.subscribe([subscription_name])
    while True:
        try:
            msg = consumer.poll(10)

        except SerializerError as e:
            logger.error("Message deserialization failed for {}: {}".format(msg, e))
            break

        if msg is None:
            continue

        if msg.error():
            logger.error("AvroConsumer error: {}".format(msg.error()))
            continue

        # Find surebets
        doc = json.loads(msg.value())
        parse_mongo_dates(doc)
        try:
            match = MatchInDB(**doc)
        except ValidationError as e:
            logger.error(f"Error generating model from Kafka event. Event: {msg.value()}")
            continue

        # We do not process surebets that has been created less than one minute ago
        if not (match.surebets
                and datetime.utcnow() - min(surebet.created_at for surebet in match.surebets) < timedelta(minutes=1)):
            surebets = SureBetsFinder(match.bets).find_all()
            if surebets:
                logger.info(f"{len(surebets)} surebets found for match '{match.slug}'")
                data = json.dumps(list(map(lambda x: x.dict(), surebets)))
                try:
                    response = requests.post(f"{apiestas_url}/api/matches/{match.slug}/surebets", data=data)
                    if response.status_code != 200:
                        logger.error(f"There was an error submitting the surebet. Data: {data}")
                except Exception:
                    logger.error(f"There was an error submitting the surebet. Data: {data}", exc_info=True)
            else:
                logger.info(f"No surebets found for match '{match.slug}'")

    consumer.close()

    def check_surebets_recency(match: MatchInDB):
        min(surebet.created_at for surebet in surebets)

