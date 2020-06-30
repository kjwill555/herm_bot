# Setup
```bash
$ git clone https://github.com/kjwill555/herm_bot.git
$ cd herm_bot
```


Then, create a virtual environment named "venv" in the `herm_bot` directory that was just created.
Activate the virtual environment.


```bash
# still inside herm_bot
(venv) $ git submodule init
(venv) $ git submodule update
(venv) $ cd discord.py
(venv) $ pip install -U .[voice]
```
