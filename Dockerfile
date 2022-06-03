FROM python:3.8.8-slim as builder

RUN apt update \
    && apt install libgl1-mesa-glx ffmpeg ghostscript imagemagick -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY deploy/ImageMagick-6/policy.xml /etc/ImageMagick-6/

WORKDIR /app
ADD . /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

EXPOSE 4444

HEALTHCHECK  --interval=10s --timeout=3s \
  CMD python3 ws_healthcheck.py

ENTRYPOINT ["python"]
CMD ["-m", "veedrive.main"]
