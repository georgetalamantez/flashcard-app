let currentFlashcards = [];
let currentIndex = 0;
let isFlipped = false;

// DOM Elements
const uploadForm = document.getElementById('upload-form');
const xmlFileInput = document.getElementById('xml-file');
const uploadBtn = document.getElementById('upload-btn');
const parserOutput = document.getElementById('parser-output');
const sectionsList = document.getElementById('sections-list');

const generateBtn = document.getElementById('generate-btn');
const cardCountInput = document.getElementById('card-count');
const modelSelect = document.getElementById('model-select');
const generationStatus = document.getElementById('generation-status');

const flashcardContainer = document.getElementById('flashcard-container');
const flashcard = document.getElementById('flashcard');
const questionText = document.getElementById('question-text');
const answerText = document.getElementById('answer-text');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const flipBtn = document.getElementById('flip-btn');
const cardCounter = document.getElementById('card-counter');

const exportJsonBtn = document.getElementById('export-json');
const exportCsvBtn = document.getElementById('export-csv');

let parsedSections = [];
let currentSourceFile = "";

// Event Listeners
uploadBtn.addEventListener('click', handleUpload);
generateBtn.addEventListener('click', handleGenerate);
prevBtn.addEventListener('click', showPrevCard);
nextBtn.addEventListener('click', showNextCard);
flipBtn.addEventListener('click', flipCard);
flashcard.addEventListener('click', flipCard);

exportJsonBtn.addEventListener('click', () => window.location.href = '/export/json');
exportCsvBtn.addEventListener('click', () => window.location.href = '/export/csv');

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    if (currentFlashcards.length === 0) return;
    
    if (e.code === 'Space') {
        e.preventDefault();
        flipCard();
    } else if (e.code === 'ArrowRight') {
        showNextCard();
    } else if (e.code === 'ArrowLeft') {
        showPrevCard();
    }
});

async function handleUpload() {
    const file = xmlFileInput.files[0];
    if (!file) {
        alert("Please select a file first.");
        return;
    }

    currentSourceFile = file.name;
    const formData = new FormData();
    formData.append('file', file);

    uploadBtn.disabled = true;
    uploadBtn.textContent = "Uploading...";

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error(await response.text());

        const data = await response.json();
        parsedSections = data.sections;
        
        displaySections(parsedSections);
        parserOutput.classList.remove('hidden');
        generateBtn.classList.remove('hidden');
    } catch (error) {
        console.error("Upload failed:", error);
        alert("Upload failed: " + error.message);
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Upload and Parse";
    }
}

function displaySections(sections) {
    sectionsList.innerHTML = '';
    sections.forEach((section, index) => {
        const li = document.createElement('li');
        li.textContent = section.heading || `Section ${index + 1}`;
        sectionsList.appendChild(li);
    });
}

async function handleGenerate() {
    if (parsedSections.length === 0) return;

    const count = cardCountInput.value;
    const model = modelSelect.value;
    
    const formData = new FormData();
    formData.append('sections', JSON.stringify(parsedSections));
    formData.append('count', count);
    formData.append('model_name', model);
    formData.append('source_file', currentSourceFile);

    generateBtn.disabled = true;
    generationStatus.classList.remove('hidden');
    generationStatus.textContent = "Generating flashcards using AI... This may take a moment.";

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error(await response.text());

        currentFlashcards = await response.json();
        currentIndex = 0;
        
        if (currentFlashcards.length > 0) {
            displayCard();
            flashcardContainer.classList.remove('hidden');
        } else {
            alert("No flashcards were generated. Check logs.");
        }
    } catch (error) {
        console.error("Generation failed:", error);
        alert("Generation failed: " + error.message);
    } finally {
        generateBtn.disabled = false;
        generationStatus.classList.add('hidden');
    }
}

function displayCard() {
    const card = currentFlashcards[currentIndex];
    questionText.textContent = card.question;
    answerText.textContent = card.answer;
    cardCounter.textContent = `Card ${currentIndex + 1} of ${currentFlashcards.length}`;
    
    // Reset flip state
    isFlipped = false;
    flashcard.classList.remove('flipped');
    
    // Update nav buttons
    prevBtn.disabled = currentIndex === 0;
    nextBtn.disabled = currentIndex === currentFlashcards.length - 1;
}

function flipCard() {
    isFlipped = !isFlipped;
    flashcard.classList.toggle('flipped');
}

function showNextCard() {
    if (currentIndex < currentFlashcards.length - 1) {
        currentIndex++;
        displayCard();
    }
}

function showPrevCard() {
    if (currentIndex > 0) {
        currentIndex--;
        displayCard();
    }
}

// Check for existing flashcards on load
async function loadExistingFlashcards() {
    try {
        const response = await fetch('/flashcards');
        if (response.ok) {
            const cards = await response.json();
            if (cards.length > 0) {
                currentFlashcards = cards;
                currentIndex = 0;
                displayCard();
                flashcardContainer.classList.remove('hidden');
            }
        }
    } catch (error) {
        console.log("No existing flashcards found or server offline");
    }
}

window.onload = loadExistingFlashcards;
