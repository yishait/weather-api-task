FROM node
WORKDIR weather_api//usr/src/app

# Install app dependencies
COPY package.json /usr/src/app/
COPY app.js /usr/src/app/

# Bundle app source
COPY . .
RUN npm install

# Start App
CMD [ "npm", "start" ]
