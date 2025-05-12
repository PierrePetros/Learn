import React from 'react';
import { Link } from 'react-router-dom';
import {BackLink} from '../components/BackLink';

function Math() {
    return (
        <div className="subject-page">
            <h1>Математика</h1>
            <div className="options">
                <Link to="/math_theory" className="option-button">Теория</Link>
                <Link to="/math_practice" className="option-button">Практика</Link>
                <Link to="/math_sandbox" className="option-button">Песочница</Link>
            </div>
            <BackLink to="/profile" />
        </div>
    );
}

export default Math;