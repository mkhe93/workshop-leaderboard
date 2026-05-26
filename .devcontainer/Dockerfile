FROM node:22-bookworm-slim

##### Execute as root user from here
WORKDIR /code
USER root:root

# Install necessary packages and clean up apt cache to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl net-tools jq ca-certificates vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

##### Set working directory
ENV CONTAINER_USER=1000
RUN mkdir -p /code && chown ${CONTAINER_USER}:${CONTAINER_USER} /code
USER ${CONTAINER_USER}:${CONTAINER_USER}

# Install UV and Python 3.13
ENV UV_INSTALL_DIR=/home/node/.local/bin
ENV PATH="/home/node/.local/bin:$PATH"
RUN curl -LsSf https://astral.sh/uv/0.10.4/install.sh | sh
RUN uv python install 3.13

RUN curl -fsSL https://claude.ai/install.sh | bash -s 2.1.142

RUN echo 'alias ll="ls -lh"' >> ~/.bashrc
RUN echo 'alias la="ls -alh"' >> ~/.bashrc
RUN echo 'alias lisa="ls -lisah"' >> ~/.bashrc
