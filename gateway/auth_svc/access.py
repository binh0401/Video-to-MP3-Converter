import os, requests

def login(request):
  auth = request.authorization

  if not auth:
    return None, ("Missing credentials", 401)
  
  basicAuth = (auth.username, auth.password)

  #Send request from API Gateway to Auth Service for login
  response = requests.post(
    f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
    auth=basicAuth
  )
  
  if response.status_code == 200:
    return response.text, None # Auth service return token if user exist
  else:
    return None, response.text # Auth service return error message if user does not exist