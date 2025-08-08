## Step 1: Dcoker install

## Step 2: Clone GitHub repository
~~~
git clone https://github.com/dai-ichiro/smolagents_gradio_gemini smolagents
cd smolagents
~~~
## Step 3: Create Docker image
~~~
docker build --force-rm=true -t agent-sandbox .
~~~
## Step 4: Install uv and run
~~~
uv venv
source .venv/bin/activate
uv pip install docker
uv run runner.py
~~~
