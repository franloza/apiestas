#!/bin/bash

set -e

echo "Starting docker ."
docker-compose  -f docker-compose.yml -f docker-compose.kafka.yml up -d --build

function clean_up {
    echo -e "\n\nSHUTTING DOWN\n\n"
    curl --output /dev/null -X DELETE http://localhost:8083/connectors/mongo-source || true
    docker-compose exec mongo /usr/bin/mongo --eval "db.dropDatabase()"
    docker-compose  -f docker-compose.yml -f docker-compose.kafka.yml down
    if [ -z "$1" ]
    then
      echo -e "Bye!\n"
    else
      echo -e $1
    fi
}

sleep 5
echo -ne "\n\nWaiting for the systems to be ready.."
function test_systems_available {
  COUNTER=0
  until $(curl --output /dev/null --silent --head --fail http://localhost:$1); do
      printf '.'
      sleep 2
      let COUNTER+=1
      if [[ $COUNTER -gt 30 ]]; then
        MSG="\nWARNING: Could not reach configured kafka system on http://localhost:$1 \nNote: This script requires curl.\n"

          if [[ "$OSTYPE" == "darwin"* ]]; then
            MSG+="\nIf using OSX please try reconfiguring Docker and increasing RAM and CPU. Then restart and try again.\n\n"
          fi

        echo -e $MSG
        clean_up "$MSG"
        exit 1
      fi
  done
}
test_systems_available 8082
test_systems_available 8083

trap clean_up EXIT

echo -e "\nConfiguring the MongoDB ReplicaSet.\n"
docker-compose exec mongo /usr/bin/mongo --eval '''if (rs.status()["ok"] == 0) {
    rsconf = {
      _id : "rs0",
      members: [
        { _id : 0, host : "mongo:27017", priority: 1.0 },
        { _id : 1, host : "mongo2:27017", priority: 0.5 },
        { _id : 2, host : "mongo3:27017", priority: 0.5 }
      ]
    };
    rs.initiate(rsconf);
}
rs.conf();'''

echo -e "\nKafka Topics:"
curl -X GET "http://localhost:8082/topics" -w "\n"

echo -e "\nKafka Connectors:"
curl -X GET "http://localhost:8083/connectors/" -w "\n"

sleep 2
echo -e "\nAdding MongoDB Kafka Source Connector for the 'apiestas.matches' collection:"
curl -X POST -H "Content-Type: application/json" --data '
  {"name": "mongo-source",
   "config": {
     "tasks.max":"1",
     "connector.class":"com.mongodb.kafka.connect.MongoSourceConnector",
     "connection.uri":"mongodb://mongo:27017,mongo2:27017,mongo3:27017",
      "errors.log.enable": "true",
     "errors.log.include.messages": "true",
     "topic.prefix":"mongo",
     "database":"apiestas",
     "collection":"matches"
}}' http://localhost:8083/connectors -w "\n"

sleep 2
echo -e "\nKafka Connectors: \n"
curl -X GET "http://localhost:8083/connectors/" -w "\n"

echo "Counting documents in 'apiestas.matches':"
docker-compose exec mongo /usr/bin/mongo apiestas --eval 'rs.slaveOk();db.matches.count()'


echo -e '''
==============================================================================================================
Examine the topics in the Kafka UI: http://localhost:9021 or http://localhost:8000/
  - The `matches` topic should have the crawled bets and matches.
  - The `mongo.apiestas.matches` topic should contain the change events.
Examine the collections:
  - In your shell run: docker-compose exec mongo /usr/bin/mongo
==============================================================================================================
Use <ctrl>-c to quit'''

read -r -d '' _ </dev/tty
