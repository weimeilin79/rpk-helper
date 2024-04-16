from langchain_community.document_loaders import WebBaseLoader
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from kafka import KafkaConsumer

REDPANDA_SERVER = "localhost:19092"

MONGODB_URI = 'mongodb://localhost:27017/?replicaSet=rs-localdev'
DB_NAME = 'demo'
COLLECTION_NAME = 'newRPK'
INDEX_NAME = 'rpkDocIndex'

consumer = KafkaConsumer(
  bootstrap_servers=REDPANDA_SERVER,
  #security_protocol="SASL_SSL",
  #sasl_mechanism="SCRAM-SHA-256",
  #sasl_plain_username="myuser",
  #sasl_plain_password="1234qwer",
  auto_offset_reset="earliest",
  #enable_auto_commit=False,
  consumer_timeout_ms=30000
)

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client[DB_NAME] 
collection = db[COLLECTION_NAME]  

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
def generate_and_store_embeddings(url, doc):
    try:
        text_splitter = RecursiveCharacterTextSplitter()
        documents = text_splitter.split_documents(doc)
        print(f"Documents: {documents}")
        MongoDBAtlasVectorSearch.from_documents(documents,embeddings,collection=collection)
    except PyMongoError as e:
        print(f"An error occurred: {e}")
    
def process_and_store_url(url):
    try:
        print(f"Processing: {url}")
        loader = WebBaseLoader(url)
        docs = loader.load()
        generate_and_store_embeddings(url,docs )
        
    except Exception as e:
        print(f"Exception when processing {url}: {e}")
\

consumer.subscribe("urls")

for message in consumer:
    url=message_str = message.value.decode('utf-8')
    process_and_store_url(url)

