# Specifies where to get the base image (Node v12 in our case) and creates a new container for it
FROM node:14

# Set working directory. Paths will be relative this WORKDIR.
WORKDIR /usr/src/app/owt-server-p2p

# Install dependencies
RUN npm install

# Specify port app runs on
EXPOSE 8095 8096 8097 8098
# Run the app
# CMD [ "node", "peerserver.js" ]