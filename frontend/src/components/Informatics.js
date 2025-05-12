import React from 'react';
import { Link } from 'react-router-dom';
import {BackLink} from '../components/BackLink';

function Informatics() {
    return (
        <div className="subject-page">
            <h1>Информатика</h1>
            <div className="options">
                <Link to="/informatics_theory" className="option-button">Теория</Link>
                <Link to="/informatics_practice" className="option-button">Практика</Link>
                <Link to="/informatics_sandbox" className="option-button">Песочница</Link>
            </div>
            <BackLink to="/profile" />
        </div>
    );
}

export default Informatics;