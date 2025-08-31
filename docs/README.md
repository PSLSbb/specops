# SpecOps Web Interface

A modern, intuitive web interface for SpecOps - the AI-powered onboarding factory.

## Features

- 🌐 **Web-based Analysis**: Analyze any GitHub repository directly in your browser
- 🎨 **Modern UI**: Clean, responsive design built with Tailwind CSS
- 📱 **Mobile Friendly**: Works perfectly on desktop, tablet, and mobile devices
- ⚡ **Real-time Results**: Get instant analysis and document generation
- 📥 **Download Documents**: Export generated tasks, FAQs, and quick start guides
- 🔗 **Direct Links**: Share analysis results with team members

## How to Use

1. **Visit the Website**: Go to your deployed GitHub Pages URL
2. **Enter Repository URL**: Paste any public GitHub repository URL
3. **Click Analyze**: Wait for the AI analysis to complete
4. **View Results**: Browse generated tasks, FAQs, and quick start guides
5. **Download**: Export documents as Markdown files

## Popular Examples

Try these popular repositories to see SpecOps in action:

- [React](https://github.com/facebook/react) - JavaScript UI library
- [VS Code](https://github.com/microsoft/vscode) - Code editor
- [Python](https://github.com/python/cpython) - Programming language
- [TensorFlow](https://github.com/tensorflow/tensorflow) - ML framework

## Deployment

### GitHub Pages (Frontend Only)

1. Enable GitHub Pages in your repository settings
2. Set source to "GitHub Actions"
3. Push changes to trigger automatic deployment

### Full Stack Deployment (Frontend + API)

#### Option 1: Vercel
1. Connect your GitHub repository to Vercel
2. Deploy automatically with the included `vercel.json` configuration
3. Update `API_BASE_URL` in `app.js` with your Vercel API URL

#### Option 2: Heroku
1. Create a new Heroku app
2. Deploy the API using the `api/` directory
3. Update `API_BASE_URL` in `app.js` with your Heroku API URL

#### Option 3: Railway/Render
1. Connect your repository to Railway or Render
2. Configure the API service using `api/app.py`
3. Update the API URL in the frontend

## Configuration

### Frontend Configuration

Edit `docs/app.js`:

```javascript
// Configuration
const API_BASE_URL = 'https://your-api-domain.com'; // Your API URL
const USE_MOCK_DATA = false; // Set to true for demo mode
```

### API Configuration

The API automatically detects if SpecOps is available and falls back to mock data if needed.

## Development

### Local Development

1. **Frontend**: Open `docs/index.html` in your browser
2. **API**: Run `python api/app.py` for local API server

### Mock vs Real Data

- **Mock Mode**: Uses predefined sample data for demonstration
- **Real Mode**: Connects to SpecOps backend for actual repository analysis

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │───▶│   Flask API     │───▶│   SpecOps Core  │
│   (GitHub Pages)│    │   (Vercel/Heroku)│    │   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technologies Used

- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Backend**: Flask, Python
- **Deployment**: GitHub Pages, Vercel
- **Analysis**: SpecOps Python library

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

This project is open source and available under the MIT License.