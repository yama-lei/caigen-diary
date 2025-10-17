# Frontend - caigeng Diary Archive

## Overview

A beautiful Vue 3 frontend for browsing and searching diary entries from Nanjing University library, featuring:
- Ancient library-inspired design
- NJU purple theme colors
- Sentiment-based filtering
- Date and month browsing
- Full-text search
- Statistics dashboard

## Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **Vite** - Next generation frontend tooling
- **TailwindCSS** - Utility-first CSS framework
- **Vue Router** - Official router for Vue.js
- **Axios** - HTTP client for API calls

## Setup

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

The app will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

Output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable Vue components
│   │   ├── DiaryCard.vue      # Individual diary entry card
│   │   ├── DatePicker.vue     # Date selection component
│   │   ├── SentimentFilter.vue # Sentiment filter buttons
│   │   └── Timeline.vue       # Timeline view of entries
│   ├── views/             # Page components
│   │   ├── Home.vue           # Main browsing page
│   │   ├── Search.vue         # Search page
│   │   └── Stats.vue          # Statistics dashboard
│   ├── api.js             # API client
│   ├── main.js            # App entry point
│   ├── App.vue            # Root component
│   └── style.css          # Global styles
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## Features

### Home Page
- Browse all diary entries in timeline format
- Filter by sentiment (正面/负面/中性)
- Filter by specific date
- Filter by month
- Random browsing

### Search Page
- Full-text search across all entries
- Real-time search results
- Keyword highlighting

### Statistics Page
- Total entry counts
- Sentiment distribution charts
- Date range information
- Monthly statistics
- Quick access links

## Design System

### Colors

- **NJU Purple**: `#6F42C1` - Primary brand color
- **Library Wood**: `#8B7355` - Ancient wood tone
- **Library Paper**: `#F5F1E8` - Old paper background
- **Library Ink**: `#2C2C2C` - Text color

### Typography

- **Serif**: Noto Serif SC for content (Chinese serif)
- **Sans**: Inter for UI elements

### Components

All components follow a consistent design language with:
- Card-based layouts
- Rounded corners
- Subtle shadows
- Smooth transitions
- Responsive design

## API Integration

The frontend connects to the backend API at `http://localhost:8000/api`

Make sure the backend server is running before starting the frontend.

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ support required

