

Start Redpanda 
```
docker compose up -d
```

Install rpk 
```
rpk topic create urls
rpk topic create question
rpk topic create airesponse
rpk topic create reference
```


Start MongoDB Atlas locally
Install the Altas CLI 
https://www.mongodb.com/docs/atlas/cli/stable/install-atlas-cli/#std-label-install-atlas-cli


Install ['mongosh'](https://www.mongodb.com/docs/mongodb-shell/install/) version 2.0 or later.

```
atlas deployments setup
```

Small catch

```
mongosh
cfg.members[0].host = 'localhost:27017'
cfg.members[0].horizons = { internal : 'mongod-local5733:27017' } 
rs.reconfig(cfg)
```


Download and install Ollama onto the available supported platforms (including Windows Subsystem for Linux)

```
ollama pull llama2
```

On Mac, the models will be download to ~/.ollama/models
On Linux (or WSL), the models will be stored at /usr/share/ollama/.ollama/models



Get the python env setting
```
python -m venv rag
source rag/bin/activate
pip install -r requirements.txt
```




Deactivate the python env setting
```
bash rag/bin/deactivate
```


Reference :
https://python.langchain.com/docs/integrations/llms/ollama/