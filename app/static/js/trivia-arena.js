const startBtn = document.querySelector('.start-btn');
const popupInfo = document.querySelector('.popup-info');
const exitBtn = document.querySelector('.exit-btn');
const main = document.querySelector('.main');
const continueBtn = document.querySelector('.continue-btn');
const quizSection = document.querySelector('.quiz-section');
const quizBox = document.querySelector('.quiz-box');
const questionText = document.querySelector('.question-text');
const optionList = document.querySelector('.option-list');
const nextBtn = document.querySelector('.next-btn');
const questionTotal = document.querySelector('.question-total');
const resultBox = document.querySelector('.result-box');
const tryAgainBtn = document.querySelector('.tryAgain-btn');
const goHomeBtn = document.querySelector('.goHome-btn');

let questionCount = 0;
let questionNumb = 1;
let questions = [];
let userScore = 0;


startBtn.onclick = () => {
  popupInfo.classList.add('active');
  main.classList.add('active');
};


exitBtn.onclick = () => {
  popupInfo.classList.remove('active');
  main.classList.remove('active');
};

continueBtn.onclick = async () => {
  quizSection.classList.add('active');
  popupInfo.classList.remove('active');
  main.classList.remove('active');
  quizBox.classList.add('active');

  
  try {
    const category = document.getElementById("category").value;
    const difficulty = document.getElementById("difficulty").value;
    const type = document.getElementById("type").value;

    
    if (!category || !difficulty || !type) {
      alert("Please select a category, difficulty, and type.");
      return;
    }

    // backend
    const response = await fetch(`/fetch_questions?category=${category}&difficulty=${difficulty}&type=${type}`);
    const data = await response.json();

    if (data.results) {
      questions = data.results;
      showQuestions(0);
      questionCounter(questionNumb);
    } else {
      alert("No questions found. Please try different options.");
    }
  } catch (error) {
    console.error("Error fetching questions:", error);
    alert("Failed to load questions. Please try different options");
  }
  headerScore();
}
tryAgainBtn.onclick = () => {
    quizBox.classList.add('active');
    nextBtn.classList.remove('active');
    resultBox.classList.remove('active');

    questionCount = 0;
    questionNumb = 1;
    userScore = 0;
    showQuestions(questionCount);
    questionCounter(questionNumb);

    headerScore();
  };

  goHomeBtn.onclick = () => {
    quizSection.classList.remove('active');
    nextBtn.classList.remove('active');
    resultBox.classList.remove('active');

    questionCount = 0;
    questionNumb = 1;
    userScore = 0;
    showQuestions(questionCount);
    questionCounter(questionNumb);

    headerScore();
  };

nextBtn.onclick = () => {
  if (questionCount < questions.length - 1) {
    questionCount++;
    showQuestions(questionCount);
    questionNumb++;
    questionCounter(questionNumb);

    nextBtn.classList.remove('active');
  } else {
    showResultBox();
  }
};


function showQuestions(index) {
  const currentQuestion = questions[index];

  questionText.textContent = `${index + 1}. ${decodeHTML(currentQuestion.question)}`;

  // Clear existing options before adding new ones
  optionList.innerHTML = '';

  // Combine correct and incorrect answers and shuffle them
  const allOptions = [...currentQuestion.incorrect_answers, currentQuestion.correct_answer];
  shuffleArray(allOptions);

  // Generate and append options dynamically
  allOptions.forEach((option, i) => {
    const optionDiv = document.createElement('div');
    optionDiv.classList.add('option');
    optionDiv.innerHTML = `<span>${String.fromCharCode(65 + i)}. ${decodeHTML(option)}</span>`;
    optionDiv.onclick = () => selectOption(optionDiv, currentQuestion.correct_answer);
    optionList.appendChild(optionDiv);
  });
}


// Shuffle an array (Fisher-Yates shuffle)
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}


// Decode HTML entities
function decodeHTML(html) {
  const textArea = document.createElement('textarea');
  textArea.innerHTML = html;
  return textArea.value;
}


function selectOption(optionElement, correctAnswer) {
    if (optionElement.textContent.includes(decodeHTML(correctAnswer))) {
      optionElement.classList.add('correct');
      userScore += 1;
      headerScore();
    //   alert('Correct Answer!');
    } else {
      optionElement.classList.add('incorrect');
    //   alert('Incorrect Answer!');
  
      // Highlight the correct answer after an incorrect selection
      document.querySelectorAll('.option').forEach(option => {
        if (option.textContent.includes(decodeHTML(correctAnswer))) {
          option.classList.add('correct');
        }
      });
    }

    nextBtn.classList.add('active');
  
    // Disable all options to prevent further clicks
    document.querySelectorAll('.option').forEach(option => {
      option.classList.add('disabled');
    });
    nextBtn.disabled = false;
  }
  
// Updating the question counter
function questionCounter(index) {
  questionTotal.textContent = `${index} of ${questions.length} Questions`;
}

function headerScore() {
    const headerScoreText = document.querySelector('.header-score');
    headerScoreText.textContent = `Score: ${userScore} / ${questions.length}`;
}

// Show the result box
function showResultBox() {
  quizBox.classList.remove('active');
  resultBox.classList.add('active');
//   quizSection.classList.remove('active');

const scoreText = document.querySelector('.score-text');
scoreText.textContent = `Your score is ${userScore} / ${questions.length}`;

const circularProgress = document.querySelector('.circular-progress');
const progressValue = document.querySelector('.progress-value');
let progresStartValue = -1;
let progressEndValue = (userScore / questions.length) * 100;
let speed = 20;

let progress = setInterval(() => {
    progresStartValue++;
    
    progressValue.textContent = `${progresStartValue}%`;
    circularProgress.style.background = `conic-gradient(#d75ce2 ${progresStartValue * 3.6}deg, rgba(255, 255, 255, .1) 0deg)`;
    
    if (progresStartValue == progressEndValue) {
        clearInterval(progress);
    }
}, speed);
}