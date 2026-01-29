FROM golang:1.22-alpine AS builder

WORKDIR /app

COPY . .

RUN go mod tidy && go build -o app .

FROM alpine:3.19

WORKDIR /app

COPY --from=builder /app/app .

EXPOSE 8000

CMD ["./app"]

