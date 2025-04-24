# Office Api Server
Personal server for what ever I need. At the moment it just has a login and then starts a webcam video stream.
i am using it to monitor my 3D printer.

## Development environment setup

- Prepare a virtual environment


         sudo apt install ustreamer
         source .venv/bin/activate
         pip install flask bcrypt opencv-python


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
