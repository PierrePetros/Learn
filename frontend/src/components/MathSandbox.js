import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {BackLink} from '../components/BackLink';

function MathSandbox() {
    const [displayValue, setDisplayValue] = useState('0');

    const handleNumberClick = (number) => {
        setDisplayValue(displayValue === '0' ? number : displayValue + number);
    };

    const handleOperatorClick = (operator) => {
        setDisplayValue(displayValue + operator);
    };

    const handleEqualsClick = () => {
        try {
            // Используйте безопасный парсер или eval только для учебных целей
            setDisplayValue(eval(displayValue).toString());
        } catch (error) {
            setDisplayValue('Error');
        }
    };

    const handleClearClick = () => {
        setDisplayValue('0');
    };

    return (
        <div className="calculator">
            <input type="text" value={displayValue} readOnly />
            <div className="calculator-grid">
                <button onClick={handleClearClick} className="span-two">AC</button>
                <button onClick={() => handleOperatorClick('/')}>/</button>
                <button onClick={() => handleOperatorClick('*')}>*</button>
                <button onClick={() => handleNumberClick('7')}>7</button>
                <button onClick={() => handleNumberClick('8')}>8</button>
                <button onClick={() => handleNumberClick('9')}>9</button>
                <button onClick={() => handleOperatorClick('-')}>-</button>
                <button onClick={() => handleNumberClick('4')}>4</button>
                <button onClick={() => handleNumberClick('5')}>5</button>
                <button onClick={() => handleNumberClick('6')}>6</button>
                <button onClick={() => handleOperatorClick('+')}>+</button>
                <button onClick={() => handleNumberClick('1')}>1</button>
                <button onClick={() => handleNumberClick('2')}>2</button>
                <button onClick={() => handleNumberClick('3')}>3</button>
                <button onClick={() => handleNumberClick('.')}>.</button>
                <button onClick={handleEqualsClick} className="span-two">=</button>
                <button onClick={() => handleNumberClick('0')} className="span-two">0</button>
            </div>
            <BackLink to="/math" />
        </div>
    );
}

export default MathSandbox;