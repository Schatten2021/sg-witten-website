THIS IS NOT THE OFFICIAL SERVER!

THIS IS JUST A PERSONAL REMAKE!

Anyways:

README.md
---
To run, install python.
### Linux
On the command line, navigate to the folder containing this project.

Install Python 3, if necessary:
`sudo apt install python3`.

Then create a Python venv using `python3 -m venv .venv` and activate it `source .venv/bin/activate`.
Afterwards install the necessary dependencies `pip install -r requirements.txt`.
Finally you can start the server by running `python main.py`.

You should see an output like this:
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
Now you can navigate to [localhost:5000](http://localhost:5000) in your browser and explore the website.
If something else shows up, close whatever process is occupying localhost:5000 and try again.
Or change the target port by changing the port keyword for the `app.run(debug=True, host=127.0.0.1, port=5000)` function call to something else, like 8000.
Then navigate to localhost:port

### Windows
Install Python from [python.org](https://www.python.org/)

Then create a Python venv by running `python -m venv .venv` and activate it with `.venv/Scripts/activate`.
Now install the dependencies like this: `pip install -r requirements.txt`.
Lastly start the server with `python main.py`.
This (should) output something like this:
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
Or change the target port by changing the port keyword for the `app.run(debug=True, host=127.0.0.1, port=5000)` function call to something else, like 8000.
Then navigate to localhost:port
