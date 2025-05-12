import React, { useState } from 'react';
import { BackLink } from '../components/BackLink';

function InformaticsSandbox() {
    const [inputText, setInputText] = useState('');
    const [outputText, setOutputText] = useState('');

    const handleInputChange = (e) => setInputText(e.target.value);

    const handleExecute = async () => {
        const token = localStorage.getItem('access_token');
        try {
            const response = await fetch('/execute_python', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ code: inputText }),
            });
            const data = await response.json();
            setOutputText(data.output);
        } catch (err) {
            setOutputText('Произошла ошибка.');
        }
    };

    return (
        <div className="sandbox-section">
            <h2>Песочница Python</h2>
            <textarea
                value={inputText}
                onChange={handleInputChange}
                placeholder="Напишите код на питоне"
            />
            <button onClick={handleExecute} className="execution-button">
                Выполнить
            </button>
            <div>
                <h3>Вывод:</h3>
                <pre>{outputText}</pre>
            </div>
            <BackLink to="/informatics" />
        </div>
    );
}

export default InformaticsSandbox;