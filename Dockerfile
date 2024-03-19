FROM python:3.12-slim

WORKDIR /Project7730
COPY . /Project7730

RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/GoodManWen/Project7730.git

WORKDIR /Project7730/qdata
RUN pip install --trusted-host pypi.python.org -r requirements.txt

WORKDIR /Project7730

ENV HOST 0.0.0.0
ENV PORT 8300

RUN printf "from qdata import QDataService\nif __name__ == '__main__':\n	server = QDataService('0.0.0.0', 8300")\n	server.run_serve()" > app.py

CMD ["sh", "-c", "python app.py --host=${HOST} --port=${PORT}"]