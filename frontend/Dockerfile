FROM node:20-alpine

WORKDIR /app

# Bağımlılıkları kopyala ve kur
COPY package.json package-lock.json* ./
RUN npm install

# Kaynak kodları kopyala
COPY . .

# Build argümanı olarak API URL'yi al
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Next.js uygulamasını derle
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
