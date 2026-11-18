FROM python:3.11-bookworm

ENTRYPOINT ["/bin/bash"]
ENV PATH="/root/.cargo/bin:$PATH"

COPY . /hsms
WORKDIR /hsms

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    pip install -v .
