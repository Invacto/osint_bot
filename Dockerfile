FROM selenium/node-chrome:latest

# Set environment variables to prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

USER root
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    vim \
    openssh-server \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy application and certificate
COPY WebScraper_V1.1 /app
WORKDIR /app
COPY WebScraper_V1.1/ca.crt /usr/local/share/ca-certificates/ca.crt
RUN update-ca-certificates

RUN pip3 install --no-cache-dir -r /app/requirements.txt

RUN mkdir /var/run/sshd
RUN echo 'root:password' | chpasswd
RUN sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
