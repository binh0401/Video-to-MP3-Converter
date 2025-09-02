import pika, json

def upload(f, fs, channel, access):
    # Step 1: Upload file to GridFS
    # Step 2: Check error, publish a message to RabbitMQ
    
  try:
    file_id = fs.put(f)
  except Exception as e:
    return "Internal Server Error", 500
  
  message = {
    "video_file_id": str(file_id),
    "mp3_file_id": None,
    "username": access['username'],
  }

  try:
    channel.basic_publish(
      exchange='',
      routing_key='video',
      body=json.dumps(message),
      properties=pika.BasicProperties(
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
      )
    )
  except Exception as e:
    # Publish failed - delete the file from GridFS
    fs.delete(file_id)
    return "Internal Server Error", 500