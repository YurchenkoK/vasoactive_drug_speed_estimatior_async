# Используем официальный образ Go
FROM golang:1.21-alpine AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем go.mod и go.sum
COPY go.mod ./

# Загружаем зависимости
RUN go mod download

# Копируем исходный код
COPY . .

# Собираем приложение
RUN go build -o async-service main.go

# Финальный образ
FROM alpine:latest

WORKDIR /root/

# Копируем бинарный файл из builder
COPY --from=builder /app/async-service .

# Открываем порт
EXPOSE 8081

# Запускаем приложение
CMD ["./async-service"]
