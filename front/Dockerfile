FROM node:20.11-slim 

USER root
RUN apt update && apt install -y git

USER node:node
WORKDIR /usr/src/app

# COPY --chown=node:node package.json yarn.lock ./
# RUN yarn install --no-progress --frozen-lockfile

EXPOSE 3000

# CMD [ "npm", "start" ]