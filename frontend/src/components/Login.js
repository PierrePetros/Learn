import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom'; // Добавляем Link

function Login({ onLogin }) {
    const [login, setLogin] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ login, password }),
            });

            const data = await response.json();

            if (response.ok) {
                if (data.access_token) {
                    localStorage.setItem('access_token', data.access_token);
                    onLogin(data.access_token);
                    navigate('/profile');
                } else {
                    setMessage(data.message || 'Login failed');
                }
            } else {
                setMessage(data.message || 'Login failed');
            }
        } catch (error) {
            setMessage('Network error');
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-form">
                <h2>Войти</h2>
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
                    <button type="submit">Войти</button>
                </form>
                {message && <p className="message">{message}</p>}
                <p className="auth-link">
                    Нет аккаунта? <Link to="/register">Создать</Link> {/* Ссылка на регистрацию */}
                </p>
            </div>
        </div>
    );
}

export default Login;
