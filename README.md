#AISG Makerspace: DVC for CD4ML - Part 2

![DVC for CD4ML - Part 2 Banner](https://makerspace.aisingapore.org/wp-content/uploads/2020/12/ShareAI-DVC-for-CD4ML-Banner-Part-2.png)

## [1. Beginning Continuous Integration](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#begin-ci)

### [Repository Set Up](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps1-repo-set-up)

Create a repository on GitHub (assuming the name `dvc-for-cd4ml`) and clone it on your local machine:
```bash
$ git clone https://github.com/<YOUR_GITHUB_USERNAME_HERE>/dvc-for-cd4ml.git
$ cd dvc-for-cd4ml
```

### [Create a GitHub Action Workflow](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps1-create-ga-workflow)

```bash
# NOTE: Run these commands from the repository's root location
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/.github/workflows/build-environment.yaml --create-dirs -o .github/workflows/build-environment.yaml
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/.github/workflows/retag-docker-image.yaml --create-dirs -o .github/workflows/retag-docker-image.yaml
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/scripts/check-file-matches.sh --create-dirs -o scripts/check-file-matches.sh
$ git add .github scripts
$ git commit -m "First commit; add GA workflows and script for building environment."
$ git push origin master
```

### [Populating GitHub Secrets](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps1-populate-github-secrets)

Add the following credentials to your repository's GitHub Secrets:
+ `DOCKERHUB_USER`: Docker Hub account username.
+ `DOCKERHUB_PW`: Docker Hub password.

### [Automating a Container (Docker) Build](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps1-auto-container-build)

+ Create a new branch `build-env`, add files into it, and push it to the remote repository:

```bash
$ git checkout -b build-env
$ git push -u origin build-env
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/docker/dvc-for-cd4ml.Dockerfile --create-dirs -o docker/dvc-for-cd4ml.Dockerfile
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/dvc-for-cd4ml-conda.yaml --create-dirs -o dvc-for-cd4ml-conda.yaml
$ git add docker dvc-for-cd4ml-conda.yaml
$ git commit -m "Add Dockerfile and Conda YAML file for building the custom dev environment."
$ git push origin build-env
```

### [Triggering a Workflow Manually](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps1-trigger-workflow-manual)

+ Take note of the commit SHA from the workflow executed above and trigger the `Change Latest Docker Image` workflow manually.

+ Make a pull request merging `build-env` into the `master` branch.

+ Switch back to the `master` branch and pull the changes locally:

```bash
$ git checkout master
$ git pull origin master
```

## [2. Automated Testing & Versioning with DVC](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#test-version-data-pipeline)

### [DVC with Remote Storage](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps2-dvc-remote-store)

+ Install the Conda environment locally:

```bash
$ conda env create -f dvc-for-cd4ml-conda.yaml -n dvc-for-cd4ml
$ conda activate dvc-for-cd4ml
```

+ Create a new branch `test-code-check-exp` and push it to remote:

```bash
$ git checkout -b test-code-check-exp
$ git push -u origin test-code-check-exp
```

+ Initialise DVC and remote storage for it:

```bash
$ dvc init
# The `.dvc` folder is automatically tracked by Git after initialisation
$ git commit -m "DVC init."
$ dvc remote add -d azremote azure://dvc-remote/dvc-for-cd4ml
$ dvc remote modify --local azremote connection_string '<PASTE YOUR CONNECTION STRING HERE>'
$ git add .dvc/config
$ git commit -m "Add remote storage for DVC."
```

### [Adding & Versioning Raw Data](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps2-add-version-raw-data)

+ Download raw data:

```bash
$ wget https://ryzalkdev.blob.core.windows.net/ryzal-pub-misc/dvc-for-cd4ml-resources/acl-imdb-movie-reviews.zip --directory-prefix=./data/raw/
$ unzip data/raw/acl-imdb-movie-reviews.zip -d data/raw
$ rm data/raw/acl-imdb-movie-reviews.zip
```

+ Add raw data to DVC and push to remote storage:

```bash
$ dvc add data/raw
$ git add data/raw.dvc data/.gitignore
$ git commit -m "Add raw data for DVC to track."
$ dvc push data/raw.dvc
```

+ Add scripts and parameter file for processing raw data:

```bash
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/src/__init__.py --create-dirs -o src/__init__.py
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/src/data_prep.py --create-dirs -o src/data_prep.py
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/params.yaml --create-dirs -o params.yaml
$ git add src/__init__.py src/data_prep.py params.yaml
$ git commit -m "Add Python scripts for data preparation and config (params) file."
```

### [DVC Pipelines](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps2-dvc-pipelines)

+ Activate Conda environment and run the data processing pipeline through DVC:

```bash
# Making sure that the conda environment has been activated
$ conda activate dvc-for-cd4ml
$ dvc run -n data_prep \
    -d src/data_prep.py -d data/raw \
    -o data/processed \
    python src/data_prep.py
```

+ Add and commit the newly created DVC artefacts:

```bash
$ git add data/.gitignore dvc.yaml dvc.lock
$ git commit -m "Add and execute data preparation pipeline to/through DVC."
```

+ Push processed raw data to remote storage for DVC:

```bash
$ dvc push data_prep
```

### [Adding & Automating Unit Tests](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps2-add-auto-unit-tests)

+ Add and commit files for running unit tests and linter:

```bash
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/tests/__init__.py --create-dirs -o tests/__init__.py
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/tests/test_data_prep.py --create-dirs -o tests/test_data_prep.py
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/.pylintrc --create-dirs -o .pylintrc
$ git add tests/__init__.py tests/test_data_prep.py .pylintrc
$ git commit -m "Add unit tests and linter configuration."
```

+ Create file for running tests and checks on GitHub Actions:

```bash
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/.github/workflows/test-analyse-code.yaml --create-dirs -o .github/workflows/test-analyse-code.yaml
```

+ Replace the username prefix `ryzalk` with your own Docker Hub username and then add and track the workflow file:

```bash
$ git add .github/workflows/test-analyse-code.yaml
$ git commit -m "Add GitHub Action workflow for running unit tests and linter."
$ git push origin test-code-check-exp
```

## [3. Reviewing Model Experiments](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#review-model-exp)

### [Experiment Tracking](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps3-exp-track)

+ Log in to Weights & Biases on your local machine:

```bash
$ wandb login <YOUR_WANDB_API_KEY>
```

+ Create, add and commit the training script:

```bash
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/src/train.py --create-dirs -o src/train.py
$ git add src/train.py
$ git commit -m "Add model training script."
```

+ Run the model experiment through DVC:

```bash
$ dvc run -n train_model \
    -d data/processed -d src/train.py \
    -o models/text-classification-model -o train-run-metrics.md \
    -p train.epochs,train.bs,train.metric,train.pretrained_embedding \
    python src/train.py
```

+ Add and commit the newly created artefacts to the repository, tag the commit, and then push to DVC remote storage:

```bash
$ git add models/.gitignore .gitignore dvc.yaml dvc.lock
$ git commit -m "Add a DVC pipeline stage for training the binary sentiment classification model."
$ git tag -a "model-v1.0" -m "First version of text classification model."
$ dvc push train_model
```

### [Reviewing Model Experiments Through Comments](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps3-review-model-exp)

+ Create the file for the GitHub Action workflow:

```bash
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/.github/workflows/comment-pull-req.yaml --create-dirs -o .github/workflows/comment-pull-req.yaml
```

+ Replace the username prefix `ryzalk` with your own Docker Hub username and then add and track the workflow file:

```bash
$ git add .github/workflows/comment-pull-req.yaml
$ git commit -m "Add GitHub action workflow for displaying model training experiment results. Trigger: comment-model-exp"
```

+ Add the Azure connection string as a GitHub secret; name it AZ_CONN_STRING.

+ Push the `test-code-check-exp` to the remote repository:

```bash
$ git push origin test-code-check-exp
```

### [Reproducing The Model Training Pipeline](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#ps3-repro-model-train-pipeline)

+ Navigate to another folder (or machine), clone the repository and reproduce the model training pipeline:

```bash
$ git clone https://github.com/<YOUR_GITHUB_USERNAME_HERE>/dvc-for-cd4ml.git
$ cd dvc-for-cd4ml
$ git checkout -b improve-model
$ git push -u origin improve-model
$ dvc remote modify --local azremote connection_string '<PASTE YOUR CONNECTION STRING HERE>'
$ dvc pull data_prep train_model
# Make sure that the relevant conda environment has been activated
$ conda activate dvc-for-cd4ml
$ dvc repro --downstream train_model
Stage 'train_model' didn't change, skipping
Data and pipelines are up to date.
```

+ Change the value for the `train.epochs` parameter in the file `params.yaml` to `5`:

```bash
$ dvc repro --downstream train_model
Running stage 'train_model' with command:
	python src/train.py
...
```

+ Add, commit, tag, and push the newly changed/created artefacts to the remote Git repository and DVC remote storage:

```bash
$ git add dvc.lock params.yaml
$ git commit -m "Train second version of sentiment classification model (5 epochs). Trigger: comment-model-exp"
$ git tag -a "model-v2.0" -m "Second version of text classification model."
$ git push origin improve-model
$ dvc push train_model
```

+ Create a pull request comparing the `improve-model` branch with `master` and merge. Pull the changes to your local branch after:

```bash
$ git checkout master
$ git pull origin master
```

+ Retrieve a previous version of the predictive model:

```bash
$ git tag
...
model-v1.0
model-v2.0
$ git checkout model-v1.0 -- dvc.lock
$ dvc checkout train_model
...
M       models/text-classification-model/
M	train-run-metrics.md
```

## [4. Packaging & Serving](https://makerspace.aisingapore.org/2020/12/data-versioning-for-cd4ml-–-part-2/#packaging)

+ Create the files for packaging and serving the model:

```bash
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/src/serve_model.py --create-dirs -o src/serve_model.py
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/docker/dfc-model-flask-server.Dockerfile --create-dirs -o docker/dfc-model-flask-server.Dockerfile
$ curl https://raw.githubusercontent.com/ryzalk/dvc-for-cd4ml/master/.dockerignore --create-dirs -o .dockerignore
```

+ Build the Docker image on your local machine:

```bash
$ docker build . -t dfc-model-flask-server:model-v1.0 -f ./docker/dfc-model-flask-server.Dockerfile
```

+ Run the container:

```bash
$ docker run -d -p 80:80 --name dfc-serving dfc-model-flask-server:model-v1.0
```

+ Test out a POST request and get a prediction:

```bash
$ curl -X POST "localhost/predict" -H "Content-Type: application/json" -d '{"text": "This movie was unpleasant, like the year 2020."}'
{"sentiment":"negative"}
```

+ Stop the container and push the files above to the remote repository:

```bash
$ docker stop dfc-serving
# To get rid of changes to the dvc.lock file
$ git checkout master -- dvc.lock
$ git add .dockerignore docker/dfc-model-flask-server.Dockerfile src/serve_model.py
$ git commit -m "Add Python script and Dockerfile for model serving."
$ git push origin master
```
