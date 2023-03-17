FROM python:3.9
ARG GITLAB
ENV GITLAB=$GITLAB
RUN git clone https://$GITLAB@git.scc.kit.edu/ipd-boehm/pse/ipd-pse-2022-ws/subspace-outlier-profiling/team-1/pse-implementation.git
WORKDIR pse-implementation
RUN apt -y update && \
    apt -y install python3-pip build-essential libsqlite3-dev && \
    apt -y upgrade && \
    pip3 install -r requirements.txt
RUN python3 manage.py makemigrations user && \
    python3 manage.py makemigrations experiment && \
    python3 manage.py migrate && \
    python3 manage.py loaddata fixtures/fixtures.json
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
