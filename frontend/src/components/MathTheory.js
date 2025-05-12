import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {BackLink} from '../components/BackLink';

function MathTheory() {
    const [theoryContent, setTheoryContent] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentPage, setCurrentPage] = useState(0);

    const itemsPerPage = 1;

    useEffect(() => {
        const fetchMathTheory = async () => {
            const token = localStorage.getItem('access_token');
            try {
                const response = await fetch('/api/math_theory', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                const data = await response.json();
                setTheoryContent(data);
            } catch (e) {
                setError(e);
            } finally {
                setLoading(false);
            }
        };

        fetchMathTheory();
    }, []);

    const goToPreviousPage = () => {
        setCurrentPage(currentPage - 1);
    };
    const goToNextPage = () => {
        setCurrentPage(currentPage + 1);
    };

    if (loading) {
        return <div className="loading-message">Загрузка теории по математике...</div>;
    }

    if (error) {
        return <div className="error-message">Ошибка: {error.message}</div>;
    }

    const startIndex = currentPage * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const displayedItems = theoryContent.slice(startIndex, endIndex);

    return (
        <div className="theory-page">
            <h1>Теория по математике</h1>
            {displayedItems.map((item) => (
                <div key={item.id} dangerouslySetInnerHTML={{ __html: item.content }} />
            ))}
            <div className="pagination">
                <button
                    onClick={goToPreviousPage}
                    disabled={currentPage === 0}
                    className="pagination-button">
                    &lt; Предыдущая
                </button>
                <button
                    onClick={goToNextPage}
                    disabled={endIndex >= theoryContent.length}
                    className="pagination-button">
                    Следующая &gt;
                </button>
            </div>
            <br></br>
            <BackLink to="/math" />
        </div>
    );
}

export default MathTheory;