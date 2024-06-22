THIS IS NOT THE OFFICIAL SERVER!

THIS IS JUST A PERSONAL REMAKE!

Anyways:

README.md
---
To run, install python.
## Installation
### Linux
On the command line, navigate to the folder containing this project.

Install Python 3, if necessary:
`sudo apt install python3`.

Then create a Python venv using `python3 -m venv .venv` and activate it `source .venv/bin/activate`.
Afterwards install the necessary dependencies `pip install -r requirements.txt`.


### Windows
Install Python from [python.org](https://www.python.org/)

Then create a Python venv by running `python -m venv .venv` and activate it with `.venv/Scripts/activate`.
Now install the dependencies like this: `pip install -r requirements.txt`.


### Afterwards

When you have everything installed, you'll need to set all the required environment variables (`MAIL_SERVER`, `MAIL_USERNAME` and `MAIL_PASSWORD`) to their respective values.

Lastly start the server with `python main.py`.
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 701-602-878
 * 
```

You can now head to [localhost:5000](http://localhost:5000) on your maschine to explore the website.
If something else shows up, close whatever process is occupying localhost:5000 and try again.
Or you can change the target port by changing the port keyword for the `app.run(debug=True, host=127.0.0.1, port=5000)` function call to something else, like 8000.
Then navigate to localhost:port

Now create an account with the name "admin" and the surname "admin". The account with this name will automatically have the admin role.


For production I recommend using gunicorn, which can be installed via pip (`pip install gunicorn`).
