import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import CommitHistory from './components/CommitHistory';
import DependencyTracker from './components/DependencyTracker';
import DocGenerator from './components/DocGenerator';
import DocumentationGen from './components/DocumentationGen';

const App = () => {
    return (
        <BrowserRouter>
            <Navbar />
            <Routes>
                <Route path='/components/DependencyTracker' element={<DependencyTracker />}/>
                <Route path='/components/CommitHistory' element={<CommitHistory />}/>
                <Route path='/components/DocGenerator' element={<DocGenerator />}/>
                <Route path='/components/DocumentationGen' element={<DocumentationGen />}/>
            </Routes>
        </BrowserRouter>
    );
}

export default App;