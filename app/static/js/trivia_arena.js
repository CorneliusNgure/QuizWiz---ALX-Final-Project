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
const scoreText = document.querySelector('.score-text');

let questionCount = 0;
let questionNumb = 1;
let questions = [];
let score = 0;

// Event handlers
startBtn.onclick = () => {
  popupInfo.classList.add('active');
  main.classList.add('active');
};

exitBtn.onclick = () => {
  popupInfo.classList.remove('active');
  main.classList.remove('active');
};

continueBtn.onclick = async () => {
  quizSection.classList.add("active");
  popupInfo.classList.remove("active");
  main.classList.remove("active");
  quizBox.classList.add("active");

  const category = document.getElementById("category").value.trim();
  const difficulty = document.getElementById("difficulty").value.trim();
  const type = document.getElementById("type").value.trim();

  if (!category || !difficulty || !type) {
    alert("Please select all quiz options before proceeding.");
    return;
  }

  try {
    const response = await fetch(
      `/fetch_questions?category=${category}&difficulty=${difficulty}&type=${type}`
    );

    if (response.ok) {
      const data = await response.json();

      if (Array.isArray(data.results) && data.results.length > 0) {
        questions = data.results.map((q, index) => ({
          ...q,
          question_id: q.id || index + 1,
        }));
        showQuestions(0);
        questionCounter(questionNumb);
      } else {
        alert("No questions found for the selected options.");
      }
    } else {
      alert("Failed to load questions. Please try again later.");
    }
  } catch (error) {
    alert("An error occurred while fetching questions.");
    console.error(error);
  }
};

nextBtn.onclick = () => {
  if (questionCount < questions.length - 1) {
    questionCount++;
    questionNumb++;
    showQuestions(questionCount);
    questionCounter(questionNumb);
    nextBtn.classList.remove('active');
  } else {
    console.log("Questions Completed!");
    showResultBox();
    setTimeout(() => {
      window.location.href = '/analytics';
    }, 3000); // Redirects after 3 seconds
  }
};

nextBtn.onclick = () => {
  if (questionCount < questions.length - 1) {
    questionCount++;
    questionNumb++;
    showQuestions(questionCount);
    questionCounter(questionNumb);
    nextBtn.classList.remove('active');
  } else {
    console.log("Questions Completed!");
    showResultBox();
    window.location.href = '/analytics'; // Redirects to the analytics page
  }
};


tryAgainBtn.onclick = resetQuiz;
goHomeBtn.onclick = resetQuiz;

function resetQuiz() {
  quizSection.classList.remove('active');
  nextBtn.classList.remove('active');
  resultBox.classList.remove('active');
  questionCount = 0;
  questionNumb = 1;
  score = 0;
  showQuestions(questionCount);
  questionCounter(questionNumb);
}

function showQuestions(index) {
  const currentQuestion = questions[index];
  questionText.textContent = `${index + 1}. ${decodeHTML(currentQuestion.question)}`;
  optionList.innerHTML = '';

  const allOptions = [...currentQuestion.incorrect_answers, currentQuestion.correct_answer];
  shuffleArray(allOptions);

  allOptions.forEach((option) => {
    const optionDiv = document.createElement('div');
    optionDiv.classList.add('option');
    optionDiv.innerHTML = `<span>${decodeHTML(option)}</span>`;
    optionDiv.onclick = () => {
      selectOption(optionDiv, currentQuestion.correct_answer);
    };
    optionList.appendChild(optionDiv);
  });
}

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

function decodeHTML(html) {
  const textArea = document.createElement('textarea');
  textArea.innerHTML = html;
  return textArea.value;
}

function selectOption(optionElement, correctAnswer) {
  const selectedAnswer = optionElement.textContent.trim();
  const currentQuestion = questions[questionCount];

  currentQuestion.selected_answer = selectedAnswer;  // Store answer for submission

  if (selectedAnswer === decodeHTML(correctAnswer)) {
    optionElement.classList.add('correct');
    score++;
  } else {
    optionElement.classList.add('incorrect');
    document.querySelectorAll('.option').forEach((option) => {
      if (option.textContent.trim() === decodeHTML(correctAnswer)) {
        option.classList.add('correct');
      }
    });
  }

  nextBtn.classList.add('active');
  document.querySelectorAll('.option').forEach((option) => option.classList.add('disabled'));
}


function questionCounter(index) {
  questionTotal.textContent = `${index} of ${questions.length} Questions`;
}

function showResultBox() {
  quizBox.classList.remove('active');
  resultBox.classList.add('active');
  scoreText.textContent = `Your score is ${score} / ${questions.length}`;

  // Prepare answers to send to backend
  const userAnswers = questions.map((q) => ({
    question_id: q.question_id,
    selected_answer: q.selected_answer || "",  // Store user’s choice
  }));

  // Send answers to backend
  fetch("/submit_quiz", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers: userAnswers }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Quiz submitted:", data);
    })
    .catch((error) => {
      console.error("Error submitting quiz:", error);
    });
}


function headerScore() {
  const headerScoreText = document.querySelector('.header-score');
  headerScoreText.textContent = `${userScore} of ${questions.length} Question`;
}



