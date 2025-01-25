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

  try {
    const category = document.getElementById("category").value.trim();
    const difficulty = document.getElementById("difficulty").value.trim();
    const type = document.getElementById("type").value.trim();

    // Validate user input
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

          console.log("Fetched questions with IDs:", questions);

          showQuestions(0); // Display the first question
          questionCounter(questionNumb); // Initialize the question counter
        } else {
          console.warn("No questions found for the provided options.", {
            category,
            difficulty,
            type,
          });
          alert("No questions found for the selected options.");
        }
      } else {
        // Handle server-side errors
        const error = await response.json();
        console.error("Server responded with an error:", error);
        alert(error.message || "An error occurred while fetching questions.");
      }
    } catch (error) {
      // Handle unexpected errors
      console.error("Unexpected error while fetching questions:", error);
      alert("Failed to load questions. Please check your connection and try again.");
    }
  } catch (error) {
    console.error("An error occurred in the quiz initialization logic:", error);
    alert("Something went wrong. Please refresh and try again.");
  }
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

tryAgainBtn.onclick = resetQuiz;
goHomeBtn.onclick = resetQuiz;

function resetQuiz() {
  quizSection.classList.remove('active');
  nextBtn.classList.remove('active');
  resultBox.classList.remove('active');
  questionCount = 0;
  questionNumb = 1;
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
  const questionIndex = questionCount;
  const selectedAnswer = optionElement.textContent.trim();

  // Store the selected answer in the corresponding question object
  questions[questionIndex].user_answer = selectedAnswer;

  if (selectedAnswer === decodeHTML(correctAnswer)) {
    optionElement.classList.add('correct');
  } else {
    optionElement.classList.add('incorrect');
    document.querySelectorAll('.option').forEach((option) => {
      if (option.textContent === decodeHTML(correctAnswer)) {
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
  console.log('Questions before submission:', questions);

  quizBox.classList.remove('active');
  resultBox.classList.add('active');

  const answers = questions.map((q) => ({
    question_id: q.question_id,
    question_text: q.question,
    user_answer: q.user_answer || '',
    correct_answer: q.correct_answer,
  }));

  console.log('Answers to submit:', answers);

  fetch('/submit_quiz', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log('Parsed data:', data);
      if (data.error) {
        alert(data.error);
        return;
      }
      const scoreText = document.querySelector('.score-text');
      scoreText.textContent = `Your score is ${data.total_score} / ${questions.length}`;
    })
    .catch((error) => console.error('Error submitting quiz:', error));
}