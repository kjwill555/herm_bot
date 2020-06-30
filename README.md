# Setup
```bash
$ git clone <insert_url>
$ cd herm_bot
```


Then, create a virtual environment named "venv" in the `herm_bot` directory that was just created.
Activate the virtual environment.


```
# still inside herm_bot
(venv) $ git submodule init
(venv) $ git submodule update
(venv) $ cd discord.py
(venv) $ pip install -U .[voice]
```
