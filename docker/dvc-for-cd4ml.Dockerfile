FROM dvcorg/cml:latest

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update

RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

COPY dvc-for-cd4ml-conda.yaml .
ARG CONDA_ENV_FILE="dvc-for-cd4ml-conda.yaml"

RUN conda update -n base -c defaults conda && \
    conda env create --file $CONDA_ENV_FILE && \
    conda clean -a -y && \
    echo "source activate dvc-for-cd4ml" >> ~/.bashrc

ENV PATH /root/miniconda3/envs/dvc-for-cd4ml/bin:$PATH
