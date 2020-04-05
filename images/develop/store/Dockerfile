FROM node:12.16.1
COPY store /app/store
RUN npm install /app/store/package.json
WORKDIR /app/store
CMD ["npx", "nodemon"]