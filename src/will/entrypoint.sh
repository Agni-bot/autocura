#!/bin/bash

# Wait for MongoDB
echo "Waiting for MongoDB..."
while ! nc -z $MONGODB_HOST $MONGODB_PORT; do
  sleep 1
done
echo "MongoDB is up!"

# Wait for Elasticsearch
echo "Waiting for Elasticsearch..."
while ! nc -z $ELASTICSEARCH_HOST $ELASTICSEARCH_PORT; do
  sleep 1
done
echo "Elasticsearch is up!"

# Initialize MongoDB collections
python -c "
from pymongo import MongoClient
client = MongoClient('$MONGODB_HOST', $MONGODB_PORT)
db = client['will_trading']
db.create_collection('trades')
db.create_collection('models')
db.create_collection('metrics')
"

# Create Elasticsearch index
curl -X PUT "http://$ELASTICSEARCH_HOST:$ELASTICSEARCH_PORT/will-logs" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "timestamp": { "type": "date" },
      "level": { "type": "keyword" },
      "message": { "type": "text" },
      "trading_pair": { "type": "keyword" },
      "action": { "type": "keyword" },
      "confidence": { "type": "float" }
    }
  }
}'

# Start the application
exec gunicorn -w 4 -b 0.0.0.0:5000 app:app 