import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import CommitHistory from './components/CommitHistory';
import DependencyTracker from './components/DependencyTracker';

const App = () => {
    return (
        <BrowserRouter>
            <Navbar />
            <Routes>
                <Route path='/components/DependencyTracker' element={<DependencyTracker />}/>
                <Route path='/components/CommitHistory' element={<CommitHistory />}/>
            </Routes>
        </BrowserRouter>
    );
}

export default App;