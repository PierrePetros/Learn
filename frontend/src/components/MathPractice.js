import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {BackLink} from '../components/BackLink';

function MathPractice() {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [userAnswer, setUserAnswer] = useState('');
    const [score, setScore] = useState(0);
    const [showResult, setShowResult] = useState(false);

    useEffect(() => {
        const fetchMathPracticeQuestions = async () => {
            const token = localStorage.getItem('access_token');
            try {
                const response = await fetch('/api/math_practice_questions', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                const data = await response.json();
                setQuestions(data);
            } catch (e) {
                setError(e);
            } finally {
                setLoading(false);
            }
        };

        fetchMathPracticeQuestions();
    }, []);

    const handleAnswerChange = (event) => {
        setUserAnswer(event.target.value);
    };

    const handleNextQuestion = () => {
        if (userAnswer.trim().toLowerCase() === questions[currentQuestion].correct_answer.toLowerCase()) {
            setScore(score + 1);
        }
        setUserAnswer('');
        if (currentQuestion < questions.length - 1) {
            setCurrentQuestion(currentQuestion + 1);
        } else {
            setShowResult(true);
        }
    };

    const handleShowResult = () => {
        if (userAnswer.trim().toLowerCase() === questions[currentQuestion].correct_answer.toLowerCase()) {
            setScore(score + 1);
        }
        setShowResult(true);
    };

    if (loading) {
        return <div className="loading-message">Загрузка вопросов для практики по математике...</div>;
    }

    if (error) {
        return <div className="error-message">Ошибка: {error.message}</div>;
    }

    if (showResult) {
        return (
            <div className="theory-page">
                <h1>Результат</h1>
                <p>Ваш результат: {score} из {questions.length}</p>
                <BackLink to="/math" />
            </div>
        );
    }

    return (
        <div className="theory-page">
            <h1>Практика по математике</h1>
            <p>{questions[currentQuestion].question_text}</p>
            <input
                type="text"
                value={userAnswer}
                onChange={handleAnswerChange}
                placeholder="Ваш ответ"
            />
            {currentQuestion < questions.length - 1 ? (
              <button onClick={handleNextQuestion} className="pagination-button">
                  Следующий вопрос
              </button>
            ) : (
              <button onClick={handleShowResult} className="pagination-button">
                  Показать результат
              </button>
            )}
            <BackLink to="/math" />
        </div>
    );
}

export default MathPractice;