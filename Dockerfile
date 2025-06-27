FROM python:3.11-alpine

# Define build-time arguments for UID and GID
ARG UID=1000
ARG GID=1000

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a non-root user with specific UID and GID
RUN addgroup -g ${GID} prod && \
    adduser -u ${UID} -G prod -s /bin/sh -D prod

WORKDIR /MechanicsBotAiogram

RUN chown -R ${UID}:${GID} /MechanicsBotAiogram && chmod 755 /MechanicsBotAiogram

COPY --chown=${UID}:${GID} requirements.txt .

RUN pip install -r requirements.txt

COPY --chown=${UID}:${GID} . .