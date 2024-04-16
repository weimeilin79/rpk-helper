from kafka import KafkaProducer
import time

# List of URLs to be sent to Kafka
urls_list = [
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-acl/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-role-assign/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-role-unassign/',
    'https://docs.redpanda.com/beta/manage/security/authentication/',
    'https://docs.redpanda.com/beta/get-started/whats-new/',
    'https://docs.redpanda.com/beta/manage/security/authentication/',
    'https://docs.redpanda.com/beta/manage/security/authorization/acl/',
    'https://docs.redpanda.com/beta/manage/security/authorization/rbac/',
    'https://docs.redpanda.com/beta/manage/security/encryption/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-acl-create/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-acl-delete/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-acl-list/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-acl-user/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-acl-user-create/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-acl-user-delete/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-acl-user-update/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-acl-user-list/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-role-create/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-role-delete/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-role-describe/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-role-list/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-role-unassign/',
    'https://docs.redpanda.com/beta/reference/rpk/rpk-security/rpk-security-role/'
]

REDPANDA_SERVER = "localhost:19092"

# Create a Kafka producer instance
producer = KafkaProducer(
    bootstrap_servers=REDPANDA_SERVER,
    # Ensure that the producer sends strings as bytes
    value_serializer=lambda v: v.encode('utf-8')
)

# Kafka topic to which the URLs will be sent
topic_name = "urls"

# Function to send each URL to the Kafka topic
def send_urls_to_kafka(urls, topic):
    for url in urls:
        # Send the URL as a message to the Kafka topic
        producer.send(topic, value=url)
        print(f"Sent URL to Redpanda Topic: {url}")
        # Wait for a short time before sending the next URL to avoid overwhelming the consumer
        time.sleep(1)

    # Ensure all messages are sent before closing the producer
    producer.flush()

# Send the URLs to Kafka
send_urls_to_kafka(urls_list, topic_name)

# Close the producer
producer.close()
print("All URLs have been sent to Kafka.")
