# 📚 Flashcard Study App

A local web application for generating AI-powered flashcards from textbook chapters using Google AI Studio.

## ✨ Features

- 📄 Upload XML/HTML textbook chapters
- 🤖 AI-powered flashcard generation using Google Gemini
- 💾 Local SQLite database (no cloud required)
- 🎴 Interactive flashcard interface with flip animation
- ⌨️ Keyboard shortcuts (Arrow keys + Spacebar)
- 📊 Export to JSON/CSV
- 🔒 Secure API key management via environment variables
- 🌐 Runs entirely on localhost

## 🛠️ Technology Stack

- **Backend**: Python 3.9+ with FastAPI
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Database**: SQLite
- **AI**: Google AI Studio (Gemini)
- **Parsing**: BeautifulSoup4 and lxml

## 📋 Prerequisites

- Python 3.9 or higher
- Google AI Studio API key ([Get one here](https://makersuite.google.com/app/apikey))
- Windows 10/11

## 🚀 Setup Instructions

### 1. Clone/Download the Project

Create a project directory and navigate to it:
```bash
mkdir flashcard-app
cd flashcard-app
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

```bash
# Windows
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your Google AI Studio API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

**Important**: Never commit your `.env` file to version control!

### 6. Start the Application

```bash
python backend/main.py
```

The application will start on `http://127.0.0.1:8000`

### 7. Open in Browser

Navigate to: `http://127.0.0.1:8000`

## 📖 Usage Guide

### Step 1: Upload Content
1. Click "Choose XML/HTML File"
2. Select your textbook chapter (`.xml`, `.html`, or `.htm`)
3. Wait for the file to be parsed

### Step 2: Generate Flashcards
1. Select the number of flashcards (use presets or custom number)
2. Click "Generate Flashcards"
3. Wait for AI generation (may take 10-30 seconds)

### Step 3: Study
1. Review flashcards using:
   - **Click "Flip Card"** or press **Spacebar** to flip
   - **"Next →"** or **Right Arrow** to go forward
   - **"← Previous"** or **Left Arrow** to go back
2. Export your flashcards:
   - **Export as JSON**: For programmatic use
   - **Export as CSV**: For spreadsheet applications

## 📁 Project Structure

```
flashcard-app/
├── backend/
│   ├── main.py              # FastAPI application
│   └── parser.py            # XML/HTML parsing logic
├── frontend/
│   ├── index.html           # Main HTML interface
│   ├── styles.css           # Styling and animations
│   └── app.js               # Frontend logic
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .env                    # Your API key (create this)
├── flashcards.db           # SQLite database (auto-created)
└── README.md               # This file
```

## 🎨 Supported File Formats

### XML Files
The parser extracts content from common XML elements:
- `<title>`, `<heading>`, `<h1>`, `<h2>`, etc.
- `<paragraph>`, `<p>`, `<para>`, `<text>`
- `<section>`, `<chapter>`, `<article>`

### HTML Files
The parser extracts:
- Headings (`<h1>` through `<h6>`)
- Paragraphs (`<p>`)
- Content grouped by sections

## 🔧 Extending the Application

The codebase is designed for easy extension:

### Add Spaced Repetition
1. Add `next_review_date` column to database
2. Implement scheduling algorithm in `backend/main.py`
3. Add review queue UI in `frontend/`

### Add Tagging System
1. Create `tags` table in database
2. Add tagging endpoints to API
3. Update UI with tag management

### Add Search Functionality
1. Implement full-text search in SQLite
2. Add search endpoint to API
3. Create search UI component

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not found"
- Ensure `.env` file exists in the root directory
- Check that the API key is properly set without quotes

### "Port 8000 already in use"
- Close other instances of the app
- Or change the port in `main.py`: `uvicorn.run(app, host="127.0.0.1", port=8001)`

### File Upload Fails
- Ensure the file is valid XML/HTML
- Check file size (very large files may timeout)
- Verify file encoding is UTF-8

### AI Generation Errors
- Verify your API key is valid
- Check your Google AI Studio quota
- Reduce the number of flashcards requested

## 🔐 Security Notes

- API keys are stored in `.env` (excluded from version control)
- Application runs locally only (no external access)
- Database is local SQLite (no cloud exposure)
- CORS is configured for local development only

## 📊 Database Schema

```sql
CREATE TABLE flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    source_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 Future Enhancements

- [ ] Spaced repetition algorithm
- [ ] Tagging system
- [ ] Search functionality
- [ ] Study session tracking
- [ ] Multiple decks support
- [ ] Progress analytics
- [ ] Dark mode
- [ ] Mobile-responsive design improvements

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the project
2. Create a feature branch
3. Submit a pull request

## 💡 Tips

- Start with 25-50 flashcards per chapter for best results
- Review the same deck multiple times for better retention
- Use descriptive filenames for source files
- Export regularly to backup your flashcards

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the Google AI Studio documentation
3. Open an issue in the repository

---

**Happy Studying! 🎓**
