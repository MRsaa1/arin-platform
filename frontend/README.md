# ARIN Frontend

Frontend приложение для ARIN Platform в корпоративном стиле SAA Alliance.

## Стиль

- **Цветовая схема**: Темная тема с золотыми акцентами
- **Логотип**: SAA Alliance стиль
- **Шрифт**: Inter (как на saa-alliance.com)

## Установка

```bash
npm install
```

## Запуск

```bash
npm run dev
```

Откройте [http://localhost:3000](http://localhost:3000)

## Структура

```
src/
├── app/              # Next.js App Router
├── components/       # React компоненты
│   ├── common/      # Общие компоненты (Header, Footer)
│   ├── agents/      # Компоненты для агентов
│   ├── risks/       # Компоненты для рисков
│   ├── graph/       # Компоненты для графа
│   └── alerts/      # Компоненты для алертов
└── lib/             # Утилиты
```



#ARIN Frontend

A frontend application for the ARIN Platform in the SAA Alliance corporate style.

## Style

- **Color scheme**: Dark theme with gold accents
- **Logo**: SAA Alliance style
- **Font**: Inter (same as saa-alliance.com)

## Installation

```bash
npm install
```

## Run

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Structure

```
src/
├── app/ # Next.js App Router
├── components/ # React components
│ ├── common/ # Common components (Header, Footer)
│ ├── agents/ # Agent-specific components
│ ├── risks/ # Risk Components
│ ├── graph/ # Graph Components
│ └── alerts/ # Alert Components
└── lib/ # Utilities
```
