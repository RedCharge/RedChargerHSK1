# Quiz Results API - Quick Reference

## Base URL
All endpoints are relative to your app's domain (e.g., `http://localhost:5000`)

## Authentication
All endpoints require user to be logged in. Include credentials with requests.

---

## Endpoints

### 1. Save Quiz Result
```
POST /api/save-quiz-result
Content-Type: application/json

Request:
{
  "quiz_type": "words" or "sentences",
  "score": number,
  "total_questions": number,
  "correct_answers": number,
  "incorrect_answers": number,
  "percentage": number (0-100),
  "time_taken": number (seconds),
  "user_answers": array of answers
}

Response (Success - 201):
{
  "success": true,
  "message": "Quiz result saved successfully",
  "quiz_id": number,
  "timestamp": "2024-01-12T10:30:45.123Z"
}

Response (Error - 400/500):
{
  "success": false,
  "error": "error message"
}
```

---

### 2. Get All Quiz Results
```
GET /api/quiz-results?limit=50&offset=0&quiz_type=words

Query Parameters:
  - limit: number of results to return (default: 50, max: 100)
  - offset: pagination offset (default: 0)
  - quiz_type: filter by 'words' or 'sentences' (optional)

Response (200):
{
  "success": true,
  "data": [
    {
      "id": 1,
      "quiz_type": "words",
      "score": 18,
      "total_questions": 20,
      "correct_answers": 18,
      "incorrect_answers": 2,
      "percentage": 90,
      "time_taken": 120,
      "user_answers": [],
      "timestamp": "2024-01-12T10:30:45.123Z",
      "date": "2024-01-12",
      "time": "10:30:45"
    },
    ...
  ],
  "total": 45,
  "limit": 50,
  "offset": 0,
  "returned": 10
}
```

---

### 3. Get Single Quiz Result
```
GET /api/quiz-results/<quiz_id>

Response (200):
{
  "success": true,
  "data": {
    "id": 1,
    "quiz_type": "words",
    "score": 18,
    "total_questions": 20,
    "correct_answers": 18,
    "incorrect_answers": 2,
    "percentage": 90,
    "time_taken": 120,
    "user_answers": [],
    "timestamp": "2024-01-12T10:30:45.123Z",
    "date": "2024-01-12",
    "time": "10:30:45"
  }
}

Response (404):
{
  "success": false,
  "error": "Quiz result not found"
}
```

---

### 4. Get Quiz Statistics
```
GET /api/quiz-stats?quiz_type=words

Query Parameters:
  - quiz_type: filter stats by 'words' or 'sentences' (optional, gets combined stats if omitted)

Response (200):
{
  "success": true,
  "data": {
    "total_quizzes": 45,
    "average_score": 17.5,
    "average_percentage": 87.5,
    "total_time": 5400,
    "best_score": 20,
    "worst_score": 12,
    "total_correct": 787,
    "total_incorrect": 113,
    "accuracy_rate": 87.44
  }
}
```

---

### 5. Get Results by Date
```
GET /api/quiz-results/by-date

Response (200):
{
  "success": true,
  "data": {
    "2024-01-12": [
      {
        "id": 45,
        "quiz_type": "words",
        "score": 18,
        "percentage": 90,
        "time": "10:30:45",
        "total_questions": 20,
        "correct_answers": 18
      },
      {
        "id": 44,
        "quiz_type": "sentences",
        "score": 19,
        "percentage": 95,
        "time": "14:15:22",
        "total_questions": 20,
        "correct_answers": 19
      }
    ],
    "2024-01-11": [
      ...
    ]
  }
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (GET request) |
| 201 | Created (POST request) |
| 400 | Bad Request (missing/invalid data) |
| 401 | Unauthorized (not logged in) |
| 404 | Not Found (quiz result doesn't exist) |
| 500 | Server Error |

---

## JavaScript Examples

### Save a quiz result
```javascript
async function saveQuizResult(quizData) {
  try {
    const response = await fetch('/api/save-quiz-result', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        quiz_type: 'words',
        score: 18,
        total_questions: 20,
        correct_answers: 18,
        incorrect_answers: 2,
        percentage: 90,
        time_taken: 120,
        user_answers: []
      })
    });
    
    const data = await response.json();
    if (data.success) {
      console.log('✅ Saved! Quiz ID:', data.quiz_id);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Get user's quiz history
```javascript
async function getQuizHistory() {
  try {
    const response = await fetch('/api/quiz-results?limit=50&quiz_type=words');
    const data = await response.json();
    
    if (data.success) {
      console.log('Total quizzes:', data.total);
      console.log('Quizzes:', data.data);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Get statistics
```javascript
async function getStats() {
  try {
    const response = await fetch('/api/quiz-stats');
    const data = await response.json();
    
    if (data.success) {
      console.log('Average Score:', data.data.average_score);
      console.log('Accuracy Rate:', data.data.accuracy_rate + '%');
      console.log('Best Score:', data.data.best_score);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Get results by date
```javascript
async function getByDate() {
  try {
    const response = await fetch('/api/quiz-results/by-date');
    const data = await response.json();
    
    if (data.success) {
      for (const [date, quizzes] of Object.entries(data.data)) {
        console.log(`${date}: ${quizzes.length} quizzes`);
      }
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Quiz results are automatically associated with the logged-in user
- Results are private - users can only access their own results
- Deleted user accounts will cascade-delete all their quiz results
- The `user_answers` array stores detailed answer information for each question
