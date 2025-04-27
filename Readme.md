# Office Api Server
Personal server for what ever I need. At the moment it has a login and then starts a webcam video stream.
At the bottom of the home page you can controll two relays controlling 2 AC sockets. 
I am using this to monitor and power off my 3D printer and a scooter charger.

## Development environment setup

- Prepare a virtual environment


         sudo apt install ustreamer
         source .venv/bin/activate
         pip install flask bcrypt opencv-python flask_socketio pyserial


- For sqlite database browser I recommend:


         sudo snap install sqlitebrowser


- Prepare a new configuration file based on "config.py.example"

- To initialize a database and create a new user:


        ./edit_user.py -h
        ./edit_user.py -a <user@email> 


- To delete a user:


        ./edit_user.py -d <user@email> 


- Run the app:


    flask --app index run --host 0.0.0.0 --port 8000 --reload
