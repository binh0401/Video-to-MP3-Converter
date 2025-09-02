import pika , sys, os, time
from send import email

#A WORKER THAT ONLY CONSUMES MESSAGES FROM THE MP3 QUEUE AND SEND NOTIFICATION TO USER




def main():

  #RabbitMQ connection
  connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
  channel = connection.channel()

  def callback(channel, method, properties, body):
    err = email.notification(body) #When receive a message, send email to user

    if err:
      #Not acknowledge the message in MP3 QUEUE if there was an error, the message still stay in queue
      channel.basic_nack(delivery_tag=method.delivery_tag)
    else:
      channel.basic_ack(delivery_tag=method.delivery_tag)


  channel.basic_consume(
    queue=os.environ.get("MP3_QUEUE"), on_message_callback=callback
  )

  print("Waiting for messages. To exit press CTRL+C")

  channel.start_consuming()


if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    print("Interrupted")
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)