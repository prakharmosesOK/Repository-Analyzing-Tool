import React from "react";
import '../styles/Navbar.css';
import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
    const location = useLocation();

    const activateClass = (pathname) => {
        if (pathname === location.pathname.toString()) {
            return 'active'
        } else {
            return 'noWork';
        }
    }

    return (
        <div className="navbarContainer">
            <ul>
                <li><Link to='/' className={activateClass('/')}>Home</Link></li>
                <li><Link to='/components/DependencyTracker' className={activateClass('/components/DependencyTracker')} >Dependency Tracker</Link></li>
                <li><Link to='/components/CommitHistory' className={activateClass('/components/CommitHistory')} >Commit History</Link></li>
                <li><Link to='/components/DocGenerator' className={activateClass('/components/DocGenerator')} >Doc Generator</Link></li>
                <li><Link to='/components/DocumentationGen' className={activateClass('/components/DocumentationGen')} >Documentation Genration</Link></li>
                <li><Link to='/about' className={activateClass('/about')}>About Section</Link></li>
            </ul>
        </div>
    );
}

export default Navbar;