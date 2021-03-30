FROM python:3.8.8 as builder

RUN apt update && apt install libgl1-mesa-glx ffmpeg ghostscript -y
COPY ./ImageMagick-6/policy.xml /etc/ImageMagick-6/

WORKDIR /app
ADD . /app

RUN pip install -r requirements.txt
RUN pip install -e .

EXPOSE 4444

CMD python ./tests/content_tests_e2e.py
