const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const { Kafka } = require('kafkajs')


const app = express();
const server = http.createServer(app);
const io = socketIo(server);


const redpanda = new Kafka({
  clientId: 'rpk-helper',
  brokers: ['localhost:19092']
})

const producer = redpanda.producer()



app.use(express.static('public'));

io.on('connection', (socket) => {
  socket.on('chat message', async (msg) => {
    await producer.connect()
    await producer.send({
      topic: 'question',
      messages: [
        { value: msg },
      ],
    })
    io.emit('Question asked', msg);
    await producer.disconnect()
  });
  
});


const consumer = redpanda.consumer({ groupId: 'rpk-group' })
const consumerReference = redpanda.consumer({ groupId: 'reference-group' })

const run = async () => {
  await consumer.connect()
  await consumerReference.connect()
  await consumer.subscribe({ topic: 'airesponse', fromBeginning: true })
  await consumerReference.subscribe({ topic: 'reference', fromBeginning: true })

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      
      console.log( "Response->",message.value.toString())
      io.emit('AI response', message.value.toString());
    },
  })

  await consumerReference.run({
    eachMessage: async ({ topic, partition, message }) => {
      console.log( "References->",message.value.toString())
      io.emit('References', message.value.toString());
    },
  })
}


run().catch(console.error)

server.listen(3000, () => {
  console.log('listening on *:3000');
});

