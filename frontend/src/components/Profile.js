import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Profile({ onLogout }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null); // Для предпросмотра
  const [selectedFile, setSelectedFile] = useState(null);   // Для отправки файла
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      const token = localStorage.getItem('access_token');
      try {
        const response = await fetch('http://localhost:5000/profile', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          if (response.status === 401) {
            navigate('/login');
            return;
          }
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setProfile(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [navigate]);

  const handleLogout = async () => {
    const token = localStorage.getItem('access_token');
    try {
      const response = await fetch('http://localhost:5000/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        onLogout();
        navigate('/login');
      } else {
        const data = await response.json();
        setError(data.message || 'Выйти не получилось');
      }
    } catch (error) {
      setError('Ошибка сети');
    }
  };

  const handleImageChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setSelectedImage(URL.createObjectURL(file));
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Выберите изображение!');
      return;
    }

    const token = localStorage.getItem('access_token');
    const formData = new FormData();
    formData.append('profilePicture', selectedFile);

    try {
      const response = await fetch('http://localhost:5000/upload_profile_picture', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        alert('Фото успешно загружено!');
        const data = await response.json();
        setProfile(data);
        setSelectedImage(null);
        setSelectedFile(null);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Не получилось загрузить фото');
      }
    } catch (error) {
      setError('Ошибка сети');
    }
  };

  const handleDeletePicture = async () => {
    const token = localStorage.getItem('access_token');

    try {
      const response = await fetch('http://localhost:5000/delete_profile_picture', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        alert('Фото профиля успешно удалено!');
        const data = await response.json();
        setProfile(data);
        setSelectedImage(null);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Не получилось удалить');
      }
    } catch (error) {
      setError('Ошибка сети');
    }
  };

  if (loading) {
    return <div className="loading-message">Загрузка профиля...</div>;
  }

  if (error) {
    return <div className="error-message">Ошибка: {error}</div>;
  }

  return (
    <div className="profile-container">
      <div className="profile-header">
        <h1>Профиль</h1>
      </div>
      <div className="profile-content">
        {profile && (
          <div className="profile-details">
            <div className="profile-picture-container">
              <img
                src={selectedImage || profile.profilePicture || 'default_profile_picture.png'}
                alt="Профиль"
                className="profile-picture"
              />
              <div className="profile-picture-actions">
                <label htmlFor="upload-input" className="back-link-short" style={{ cursor: 'pointer' }}>
                  Загрузить фото
                </label>
                <input
                  id="upload-input"
                  type="file"
                  accept="image/*"
                  style={{ display: 'none' }}
                  onChange={handleImageChange}
                />
                {selectedFile && (
                  <button className="back-link-short" onClick={handleUpload} style={{ marginTop: '10px' }}>
                    Сохранить
                  </button>
                )}
                {profile.profilePicture && (
                  <button className="back-link-short" onClick={handleDeletePicture} style={{ marginTop: '10px' }}>
                    Удалить фото
                  </button>
                )}
              </div>
            </div>
            <p>Логин: {profile.login}</p>
            <p>Имя: {profile.firstName}</p>
            <p>Фамилия: {profile.lastName}</p>
          </div>
        )}
        {/* Заменили ссылки на кнопки */}
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '2rem' }}>
          <button
            className="back-link-short"
            onClick={() => navigate('/math')}
          >
            Математика
          </button>
          <button
            className="back-link-short"
            onClick={() => navigate('/informatics')}
          >
            Информатика
          </button>
        </div>
      </div>
      <div className="profile-actions" style={{ marginTop: '2rem', textAlign: 'center' }}>
        <button className="back-link-short" onClick={handleLogout}>Выйти</button>
      </div>
    </div>
  );
}

export default Profile;