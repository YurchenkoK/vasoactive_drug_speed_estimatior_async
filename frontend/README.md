# Фронтенд приложения "Вазоактивные препараты"

## Описание
React приложение для управления каталогом вазоактивных препаратов.

## Технологии
- React 19
- TypeScript
- React Router DOM
- React Bootstrap
- Vite

## Установка

```bash
npm install
```

## Запуск

### Режим разработки
```bash
npm run dev
```

Приложение будет доступно по адресу: http://localhost:3000

### Сборка для production
```bash
npm run build
```

### Предпросмотр production сборки
```bash
npm run preview
```

## Структура проекта

```
frontend/
├── public/              # Статические файлы
│   └── placeholder-drug.svg  # Изображение по умолчанию
├── src/
│   ├── components/      # React компоненты
│   │   ├── AppNavbar.tsx
│   │   ├── Breadcrumbs.tsx
│   │   └── DrugCard.tsx
│   ├── pages/          # Страницы приложения
│   │   ├── HomePage.tsx
│   │   ├── DrugsPage.tsx
│   │   └── DrugDetailPage.tsx
│   ├── mock/           # Mock данные
│   │   └── DrugMock.ts
│   ├── DrugTypes.ts    # TypeScript типы
│   ├── drugsApi.ts     # API функции
│   ├── App.tsx         # Главный компонент
│   ├── main.tsx        # Точка входа
│   └── index.css       # Глобальные стили
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Особенности

### Фильтрация
- По названию препарата
- По минимальной концентрации
- По максимальной концентрации

### Mock данные
Приложение автоматически использует mock данные при отсутствии связи с backend.

### Proxy
Все запросы к `/api` проксируются на `http://127.0.0.1:8000` (Django backend).

## API Endpoints

- `GET /api/drugs/` - Список всех препаратов
- `GET /api/drugs/:id/` - Детальная информация о препарате
- Query параметры для фильтрации:
  - `name` - поиск по названию
  - `concentration_min` - минимальная концентрация
  - `concentration_max` - максимальная концентрация
