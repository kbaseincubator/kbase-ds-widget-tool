FROM python:3.12
LABEL org.opencontainers.image.authors="KBase Developer"

RUN apt update -y

# # Install poetry; we can install via apt-get, but that does not give us control over the version
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.2.0

# # Ensure standard path including local binaries (where poetry was installed)
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.local/bin
ENV PYTHONPATH=/kb/module/src

# #
# # Install Python dependencies
# #

# # Creates temporary directory from which to install python dependencies
RUN mkdir -p /kb/tmp

# Copy the poetry configs over
COPY pyproject.toml /kb/tmp
COPY poetry.toml /kb/tmp
COPY poetry.lock /kb/tmp
RUN cd /kb/tmp && POETRY_VIRTUALENVS_CREATE=false poetry install

# # Install service code
COPY ./ /kb/module
WORKDIR /kb/module
RUN rm -rf /kb/tmp && \
    mkdir -p /kb/module/work && \
    chmod -R a+rw /kb/module 

ENTRYPOINT [ "/bin/bash", "-l", "-c" ]
CMD [ 'python', 'src/help.py' ]
