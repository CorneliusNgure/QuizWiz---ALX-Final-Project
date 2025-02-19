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
  const selectedOption = document.querySelector(".option.selected");

  if (!selectedOption) {
    alert("Please select an answer before proceeding.");
    return;
  }

  // Store both question_id and selected_answer in the questions array
  questions[questionCount].selected_answer = selectedOption.textContent.trim();

  if (questionCount < questions.length - 1) {
    questionCount++;
    questionNumb++;
    showQuestions(questionCount);
    questionCounter(questionNumb);
    nextBtn.classList.remove("active");

    // If it's the last question, change "Next" to "Submit"
    if (questionCount === questions.length - 1) {
      nextBtn.textContent = "Submit";
    }
  } else {
    // Send answers to backend before redirecting
    submitAnswers(questions);
  }
};

// Function to submit answers
function submitAnswers(questions) {
  // Prepare the data in the format the backend expects
  const answersPayload = questions.map(q => ({
    question_id: q.id,  // Make sure the question object has an `id` field
    selected_answer: q.selected_answer
  }));

  fetch("/submit_quiz", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ answers: answersPayload })  // Match backend expectation
  })
  .then(response => response.json())
  .then(data => {
    if (data.message) {
      console.log("Answers submitted successfully!", data);
      window.location.href = "/analytics";  // Redirect after successful submission
    } else {
      console.error("Failed to submit answers:", data.error);
      alert("There was an error submitting your answers: " + data.error);
    }
  })
  .catch(error => {
    console.error("Error:", error);
    alert("There was an error submitting your answers. Please try again.");
  });
}

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

  // Remove 'selected' from any previously selected option
  document.querySelectorAll('.option').forEach((option) => {
    option.classList.remove('selected');
  });

  // Add 'selected' class to the clicked option
  optionElement.classList.add('selected');

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
  quizBox.classList.remove("active");
  resultBox.classList.add("active");

  // Prepare answers for submission
  const userAnswers = questions.map((q) => ({
    question_id: q.question_id,
    selected_answer: q.selected_answer || "", // Ensure there's always a value
  }));

  // Prevent sending empty answers
  if (userAnswers.length === 0) {
    console.error("No answers recorded.");
    return;
  }

  // Send answers to backend
  fetch("/submit_quiz", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers: userAnswers }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Quiz submitted:", data);

      if (data.total_score !== undefined) {
        // Update the result box with the score from the backend
        scoreText.textContent = `Your final score is ${data.total_score}`;
      } else {
        scoreText.textContent = "Quiz submitted, but no score received.";
      }
    })
    .catch((error) => {
      console.error("Error submitting quiz:", error);
      scoreText.textContent = "Error submitting quiz. Please try again.";
    });
}


function headerScore() {
  const headerScoreText = document.querySelector('.header-score');
  headerScoreText.textContent = `${userScore} of ${questions.length} Question`;
}



