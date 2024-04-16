from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from kafka import KafkaConsumer,KafkaProducer
import json

MONGODB_URI = 'mongodb://localhost:27017/?replicaSet=rs-localdev'
DB_NAME = 'demo'
COLLECTION_NAME = 'newRPK'
INDEX_NAME = 'rpkDocIndex'

REDPANDA_SERVER = "localhost:19092"


# Create a Kafka consumer
consumer = KafkaConsumer(
    'question',  # Kafka topic to consume from
    bootstrap_servers=REDPANDA_SERVER,  # replace with your Kafka address
    group_id='reference-bot',
    value_deserializer=lambda x: x.decode('utf-8')  # decode messages from bytes to string
)

# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers=REDPANDA_SERVER,  # replace with your Kafka address
    value_serializer=lambda x: json.dumps(x).encode('utf-8')   # encode messages from string to bytes
)


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

llm = Ollama(
    model="llama2", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

# Initialize the Vector Store
vector_search = MongoDBAtlasVectorSearch.from_connection_string(
    REDPANDA_SERVER,
    DB_NAME + "." + COLLECTION_NAME,
    embeddings,
    index_name=INDEX_NAME,
)

def query_data(query):
    # Query the data
    
    docs = vector_search.similarity_search_with_score(query, K=5)
    # For each document...
    for doc in docs:
        # Filter the document to only include the 'source', 'title', and 'description' keys
        #filtered_doc = {k: doc[k] for k in ('source', 'title', 'description')}
        document, score = doc  # Unpack the tuple
        title = document.metadata['title'].replace(" | Redpanda Docs", "")  # Remove "| Redpanda Docs" from the title
        source = document.metadata['source']

        # Create a dictionary
        reference = {
            'title': title,
            'source': source,
            'score': score
        }

        
        referenceJson = json.dumps(reference)
        
        print(f"referenceJson: {referenceJson}")
        # Send the JSON string to the Kafka topic
        producer.send('reference', referenceJson)
    return docs

try:
    for message in consumer:
        # Extract the question from the message value
        question = message.value
        print(f"Received question for reference search: {question}")
        # Query the data with the question
        references = query_data(question)
        
except KeyboardInterrupt:
    pass

finally:
    # Close the consumer
    consumer.close()