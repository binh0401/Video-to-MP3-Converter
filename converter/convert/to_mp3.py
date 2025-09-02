import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor


def start(message, fs_videos, fs_mp3s, channel):
  message = json.loads(message)

  # Empty temporary file
  tf = tempfile.NamedTemporaryFile()

  #Video contents
  out = fs_videos.get(ObjectId(message["video_file_id"])).read()

  #Add video contents to empty temporary file
  tf.write(out)

  #Create audio from temporary file
  audio = moviepy.editor.VideoFileClip(tf.name).audio

  tf.close()  #Close temporary file

  #Temporary file automatically deleted when closed


  #Write audio to the file

  #Create a new temporary file path for the mp3
  tf_path = tempfile.gettempdir() + f"/{message['video_file_id']}.mp3"  

  #Write the audio to the new file path
  audio.write_audiofile(tf_path)

  #Save the .mp3 file to GridFS
  f = open(tf_path, "rb")
  data = f.read()
  file_id = fs_mp3s.put(data)
  f.close()
  os.remove(tf_path)  #Remove the temporary mp3 file


  message["mp3_file_id"] = str(file_id)

  try:
    channel.basic_publish(
      exchange="",
      routing_key=os.environ.get("MP3_QUEUE"),
      body=json.dumps(message),
      properties=pika.BasicProperties(
        delivery_mode=pika.soec.PERSISTENT_DELIVERY_MODE,  
      ),
    )
  except Exception as e:
    fs_mp3s.delete(file_id)  #Delete the mp3 from GridFS if there was an error in RabbitMQ
    return "Error publishing message to RabbitMQ"





