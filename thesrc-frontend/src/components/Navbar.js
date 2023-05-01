import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import '../styles/Navbar.css';
import Logo from '../assets/CMU.png';

export default function Navbar() {
 
 
  return (
    <div className="navbar">
      <div className="leftSide">
        <img src={Logo} alt="CMU logo" />
        <span> &nbsp; </span>
        <h1 className="dashboard-header1">Live Dashboard</h1>
      </div>
      <div className="rightSide">
      </div>
    </div>
  );
}
