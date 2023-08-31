FROM python:3.11.2

WORKDIR /app/

COPY req.txt .

RUN sed -i.bak 's/us-west-2\.ec2\.//' /etc/apt/sources.list && \
    apt -qq update && apt -qq upgrade -y && \
    apt -qq install -y --no-install-recommends \
    apt-utils \
    curl \
    git \
    wget && \
    pip install -U pip setuptools wheel && \
    pip install -r req.txt && \
    rm req.txt && \
    git config --global user.email "98635854+thedragonsinn@users.noreply.github.com" && \
    git config --global user.name "thedragonsinn"

EXPOSE 8080 
 
CMD bash -c "$(curl -fsSL https://raw.githubusercontent.com/thedragonsinn/design_verse_bot/main/docker_start_cmd)"