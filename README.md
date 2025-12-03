# MugShot Studio

Transform your photos into high-definition, AI-crafted thumbnails in seconds.

<img width="1861" height="929" alt="image" src="https://github.com/user-attachments/assets/4d6ee2e9-2581-4145-a384-40b4345fdfdf" />
<img width="1703" height="889" alt="image" src="https://github.com/user-attachments/assets/2faa33d7-b48a-4fd7-96b5-d883a43f03ed" />


MugShot Studio is an innovative AI-powered platform that converts your regular photos into professional-quality thumbnails. Leveraging cutting-edge artificial intelligence, our service delivers stunning results in just seconds.

## Features

- **AI-Powered Transformation**: Advanced algorithms convert standard photos into professional thumbnails
- **Ultra HD Output**: Generate 4K quality images for the best visual experience
- **Fast Processing**: Transform your photos in just 5 seconds
- **Multiple Platform Presets**: Choose from 10+ platform-specific presets for optimal results
- **User-Friendly Interface**: Intuitive design makes professional photo editing accessible to everyone

## Chat Page:
<img width="1919" height="929" alt="image" src="https://github.com/user-attachments/assets/8398e1f7-61ac-4da8-9dc8-103ae422ffd8" />

## Technology Stack

### Frontend
- **Next.js 16** - React framework for production
- **TypeScript** - Strongly typed programming language
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library for React
- **Three.js** - 3D graphics library
- **shadcn/ui** - Reusable component library

### Backend
- **Python** - Programming language
- **FastAPI** - Modern, fast web framework
- **Supabase** - Open source Firebase alternative
- **Celery** - Distributed task queue

### AI Services
- **OpenAI GPT** - Text generation and processing
- **Gemini** - Multimodal AI model
- **Claude** - Conversational AI
- **Fal.ai** - Image generation services
- **ByteDance** - AI-powered services

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.8+
- npm or yarn
- Docker (optional, for containerization)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/mugshot-studio.git
   cd mugshot-studio
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

3. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python app/main.py
   ```
   The backend API will be available at `http://localhost:8000`

### Environment Variables

Create a `.env` file in both frontend and backend directories with the required API keys and configuration values.

## Project Structure

```
mugshot-studio/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/              # App router pages
│   │   ├── components/       # React components
│   │   └── lib/              # Utility functions
│   └── public/               # Static assets
├── backend/                  # Python backend API
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core configuration
│   │   ├── db/               # Database utilities
│   │   ├── services/         # External service integrations
│   │   └── utils/            # Utility functions
│   └── worker.py             # Background task worker
├── docs/                     # Documentation files
└── README.md                 # This file
```

## Development

### Frontend Development
```bash
cd frontend
npm run dev      # Start development server
npm run build    # Create production build
npm run lint     # Run ESLint
```

### Backend Development
```bash
cd backend
python app/main.py    # Start API server
celery -A worker worker --loglevel=info   # Start worker process
```

## Deployment

### Frontend Deployment
The frontend can be deployed to any static hosting service like Vercel, Netlify, or AWS S3.

### Backend Deployment
The backend can be deployed using Docker containers on platforms like AWS ECS, Google Cloud Run, or Azure Container Instances.

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For support or inquiries, please open an issue on GitHub or contact the development team.

## Acknowledgments

- Thanks to all the open-source projects that made this possible
- Special recognition to the AI services that power our platform
