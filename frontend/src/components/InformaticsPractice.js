import React, { useState, useEffect } from 'react';
import { BackLink } from '../components/BackLink'; // убедитесь, что правильный путь

function InformaticsPractice() {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [userAnswer, setUserAnswer] = useState('');
    const [score, setScore] = useState(0);
    const [showResult, setShowResult] = useState(false);

    useEffect(() => {
        const fetchQuestions = async () => {
            const token = localStorage.getItem('access_token');
            try {
                const response = await fetch('/api/informatics_practice_questions', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                const data = await response.json();
                setQuestions(data);
            } catch (e) {
                setError(e);
            } finally {
                setLoading(false);
            }
        };
        fetchQuestions();
    }, []);

    const handleAnswerChange = (e) => setUserAnswer(e.target.value);

    const handleNextQuestion = () => {
        if (
            userAnswer.trim().toLowerCase() ===
            questions[currentQuestion].correct_answer.toLowerCase()
        ) {
            setScore((prev) => prev + 1);
        }
        setUserAnswer('');
        if (currentQuestion < questions.length - 1) {
            setCurrentQuestion((prev) => prev + 1);
        } else {
            setShowResult(true);
        }
    };

    const handleShowResult = () => {
        if (
            userAnswer.trim().toLowerCase() ===
            questions[currentQuestion].correct_answer.toLowerCase()
        ) {
            setScore((prev) => prev + 1);
        }
        setShowResult(true);
    };

    if (loading) {
        return <div className="loading-message">Загрузка вопросов для практики по информатике...</div>;
    }

    if (error) {
        return <div className="error-message">Ошибка: {error.message}</div>;
    }

    if (showResult) {
        return (
            <div className="theory-page">
                <h1>Результат</h1>
                <p>
                    Ваш результат: {score} из {questions.length}
                </p>
                <BackLink to="/informatics" />
            </div>
        );
    }

    return (
        <div className="theory-page">
            <h1>Практика по информатике</h1>
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
            <BackLink to="/informatics" />
        </div>
    );
}

export default InformaticsPractice;