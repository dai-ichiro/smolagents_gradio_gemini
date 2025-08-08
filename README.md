~~~
git clone https://github.com/dai-ichiro/smolagents_gradio_gemini smolagents
cd smolagents
~~~

~~~
docker build --force-rm=true -t agent-sandbox .
~~~

~~~
uv venv
source .venv/bin/activate
uv pip install docker
uv run runner.py
~~~
