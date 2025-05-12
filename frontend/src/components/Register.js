import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';  // Добавляем Link

function Register() {
    const [login, setLogin] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ login, password, firstName, lastName }),
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(data.message || 'Успешно!');
                navigate('/login');
            } else {
                setMessage(data.message || 'Не получилось');
            }

        } catch (error) {
            setMessage('Network error');
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-form">
                <h2>Регистрция</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Логин"
                        value={login}
                        onChange={(e) => setLogin(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="Пароль"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <input
                        type="text"
                        placeholder="Имя"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                    />
                    <input
                        type="text"
                        placeholder="Фамилия"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                    />
                    <button type="submit">Создать аккаунт</button>
                </form>
                {message && <p className="message">{message}</p>}
                <p className="auth-link">
                    Уже есть аккаунт? <Link to="/login">Войти</Link> {/* Ссылка на вход */}
                </p>
            </div>
        </div>
    );
}

export default Register;
