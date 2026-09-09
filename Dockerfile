FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir '.[plot]'
COPY examples ./examples
COPY data ./data
RUN useradd --create-home ultradevice && mkdir /app/outputs && chown ultradevice /app/outputs
USER ultradevice
ENTRYPOINT ["ultradevice"]
CMD ["--help"]
