from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_mongodb import MongoDBAtlasVectorSearch
#from langchain.chains import LLMChain
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from kafka import KafkaConsumer,KafkaProducer

MONGODB_URI = 'mongodb://localhost:27017/?replicaSet=rs-localdev'
DB_NAME = 'demo'
COLLECTION_NAME = 'newRPK'
INDEX_NAME = 'rpkDocIndex'
REDPANDA_SERVER = "localhost:19092"


# Create a Kafka consumer
consumer = KafkaConsumer(
    'question',  # Kafka topic to consume from
    bootstrap_servers=REDPANDA_SERVER,  # replace with your Kafka address
    group_id='answer-bot',
    value_deserializer=lambda x: x.decode('utf-8')  # decode messages from bytes to string
)

# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers=REDPANDA_SERVER,  # replace with your Kafka address
    value_serializer=lambda x: x.encode('utf-8')  # encode messages from string to bytes
)


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

llm = Ollama(
    model="llama2", callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
)

# Initialize the Vector Store
vector_search = MongoDBAtlasVectorSearch.from_connection_string(
    MONGODB_URI,
    DB_NAME+ "." + COLLECTION_NAME,
    embeddings,
    index_name=INDEX_NAME,
)

def query_data(query):
    
    qa_retriever = vector_search.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10},
    )
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=qa_retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )

    docs = qa({"query": query})
    return docs

prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
"""
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)


try:
    for message in consumer:
        # Extract the question from the message value
        question = message.value
        print(f"Received question: {question}")
        # Query the data with the question
        llmResult = query_data(question)
        print(llmResult["result"])
        producer.send('airesponse', llmResult["result"])

except KeyboardInterrupt:
    pass

finally:
    # Close the consumer
    consumer.close()