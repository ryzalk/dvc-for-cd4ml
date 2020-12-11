FROM continuumio/miniconda3:4.8.2

RUN apt-get update && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

COPY dvc-for-cd4ml-conda.yaml .
ARG CONDA_ENV_FILE="dvc-for-cd4ml-conda.yaml"

RUN conda update -n base -c defaults conda && \
    conda env create --file $CONDA_ENV_FILE && \
    conda clean -a -y && \
    echo "source activate dvc-for-cd4ml" >> ~/.bashrc

COPY src/serve_model.py src/serve_model.py
COPY models/text-classification-model models/text-classification-model

ENTRYPOINT ["conda", "run", "-n", "dvc-for-cd4ml"]
CMD ["python", "src/serve_model.py"]
