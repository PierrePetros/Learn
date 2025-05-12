// src/components/BackLink.js
import React from 'react';
import { Link } from 'react-router-dom';

export const BackLink = ({ to }) => (
  <Link to={to} className="back-link-short">
    Назад
  </Link>
);