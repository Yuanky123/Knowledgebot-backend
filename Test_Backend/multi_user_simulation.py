import requests
import arg

def login(Current_context):
    print("Logging in...")
    
    # POST /users/login - 设置登录获得token
    login_payload = {
        'username': 'testbot1',
        'password': 'test'
    }
    
    try:
        login_response = requests.post(f"{arg.FRONTEND_URL}/users/login", json=login_payload)
        login_response.raise_for_status()  # Raise an exception for bad status codes
        
        result = login_response.json()
        
        # Extract and print the required fields
        if 'user' in result and 'selectedsubreddit' in result['user']:
            print(f"Selected Subreddit: {result['user']['selectedsubreddit']}")
        
        if 'token' in result:
            print(f"Token: {result['token']}")
            Current_context['token'] = result['token']
        
    except requests.exceptions.RequestException as e:
        print(f"Error making login request: {e}")
    
    return Current_context

def make_api_request(method, url, Current_context, headers=None, json_data=None, retry_on_auth_error=True):
    print(f"Making {method} request to {url}")
    # global Current_context
    
    # Set default headers if not provided
    if headers is None:
        headers = {}
    
    # Add authorization header if token exists
    if Current_context.get('token'):
        headers['Authorization'] = f'Bearer {Current_context["token"]}'
    
    # Make the initial request
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=json_data)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, json=json_data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Check for authentication errors
        if retry_on_auth_error and response.status_code in [401, 403]:
            print(f"Authentication error ({response.status_code}), attempting to re-login...")
            
            # Try to re-login
            login()
            
            # If we have a new token, retry the request
            if Current_context.get('token'):
                headers['Authorization'] = f'Bearer {Current_context["token"]}'
                
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=headers, json=json_data)
                elif method.upper() == 'PUT':
                    response = requests.put(url, headers=headers, json=json_data)
                elif method.upper() == 'DELETE':
                    response = requests.delete(url, headers=headers)
                
                print(f"Re-authenticated request completed with status: {response.status_code}")
            else:
                print("Re-login failed, cannot retry request")
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise



import threading


def create_thread(i):
    Current_context = {
        'post': {},
    }

    Current_context = login(Current_context)

    post_response = make_api_request('GET', f"{arg.FRONTEND_URL}/posts", Current_context)

    if post_response.status_code == 200:
        post_data = post_response.json()
        if len(post_data) > 0:
            Current_context['post']['title'] = post_data[0]['title']
            Current_context['post']['body'] = post_data[0]['body']
            Current_context['post']['id'] = post_data[0]['id']
            Current_context['post']['author_name'] = post_data[0]['author_name']
            # print(f"Post loaded: {Current_context['post']['title']}")
        else:
            print("No post found in response")
    else:
        print(f"Failed to get posts, status code: {post_response.status_code}")

    # post comments
    for comment_id in range(10):
        response = {
                    'body': f"test comment {comment_id} from thread {i}",
                    'post_id': Current_context['post']['id'],
                    'parent_comment_id': None,
                }

        make_api_request('POST', f"{arg.FRONTEND_URL}/comments", Current_context, json_data=response)

NUM_THREADS = 60
threads = []
for i in range(NUM_THREADS):
    thread = threading.Thread(target=create_thread, args=(i,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
