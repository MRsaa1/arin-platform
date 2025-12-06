# ARIN Dashboard - Корпоративный стиль SAA Alliance

## Цветовая схема

### Основные цвета
- **Фон**: `#1a1a1a` (saa-dark) - основной темный фон
- **Header**: `#0f0f0f` (saa-darker) - еще темнее для header
- **Золотой акцент**: `#CBA135` (saa-gold) - точный цвет с saa-alliance.com
- **Темный золотой**: `#8B6F47` (saa-gold-dark) - для hover эффектов
- **Белый текст**: `#FFFFFF` (saa-white)
- **Серый для карточек**: `#2a2a2a` (saa-gray)
- **Границы**: `#404040` (saa-border)

### Использование цветов
```css
/* Основной фон */
background: #1a1a1a;

/* Header */
background: #0f0f0f;

/* Акценты и кнопки */
color: #CBA135;
border-color: #CBA135;

/* Карточки */
background: #2a2a2a;
border: 1px solid #404040;
```

## Логотип

### Структура
```
SAA Alliance | ARIN
```

- **SAA Alliance**: Белый текст, жирный шрифт (font-weight: 700)
- **Разделитель**: Вертикальная линия (#404040)
- **ARIN**: Золотой текст (#CBA135), полужирный (font-weight: 600)

### Размеры
- SAA Alliance: text-2xl (28px)
- ARIN: text-lg (18px)
- Разделитель: h-6 w-px

## Типографика

### Шрифт
- **Основной**: Inter (как на saa-alliance.com)
- **Заголовки**: font-weight: 700-800
- **Текст**: font-weight: 400-500

### Размеры
- Hero заголовок: text-5xl md:text-6xl
- Заголовки разделов: text-3xl
- Подзаголовки: text-xl
- Обычный текст: text-sm-base

## Компоненты

### Header
- Темный фон (#0f0f0f)
- Белая навигация
- Золотая линия-разделитель внизу
- Кнопки "Sign in" и "Get Access" в стиле сайта

### Карточки (Cards)
- Фон: #2a2a2a
- Граница: 1px solid #404040
- Hover: border-color меняется на #CBA135
- Тень при hover: rgba(203, 161, 53, 0.2)

### Кнопки
- **Primary**: Золотой фон (#CBA135), темный текст
- **Secondary**: Прозрачный фон, белая граница, белый текст
- Hover эффекты с трансформацией

### Золотая линия
- Градиент: transparent -> #CBA135 -> transparent
- Высота: 1px
- Используется как разделитель

## Примеры использования

### Header компонент
```tsx
<header className="bg-saa-darker border-b border-saa-border">
  <Logo />
  <nav>...</nav>
</header>
```

### Карточка
```tsx
<div className="saa-card">
  {/* Контент */}
</div>
```

### Кнопка
```tsx
<button className="saa-button">
  Get Access
</button>
```

## Соответствие с saa-alliance.com

✅ Темная тема
✅ Золотые акценты (#CBA135)
✅ Логотип "SAA Alliance"
✅ Профессиональный корпоративный стиль
✅ Inter шрифт
✅ Золотая линия-разделитель
✅ Кнопки в стиле сайта

