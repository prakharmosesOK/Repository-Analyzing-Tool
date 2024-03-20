import React, { useState } from 'react';
import axios from 'axios';
import '../styles/DependencyTracker.css';

const DependencyTracker = () => {
    // Intialising variables
    const [searchItem, setSearchItem] = useState('');
    const [dependencyOutput, setDependencyOutput] = useState('');

    // Defining functions
    const handleSearchTextChange = (event) => {
        setSearchItem(event.target.value);
    }

    const handleDependencySubmit = async (event) => {
        event.preventDefault();
        const response = await axios.post("http://127.0.0.1:8000/repoanalyze/get_dependencies/", {
            input: searchItem,
        });
        console.log(response.data.output);
        setDependencyOutput(response.data.output);
    }

    const handleDependencyOutput = (event) => {
        setDependencyOutput(event.target.value);
    }

    return (
        <div className="dependencyTrackerContainer">
            <form onSubmit={handleDependencySubmit}>
                <input
                    type="text"
                    value={searchItem}
                    onChange={handleSearchTextChange}
                    placeholder='Enter the GitHub repository link here'
                />
                <button type='submit'>Submit</button>
            </form>
            <div className="output">
                <textarea
                    value={dependencyOutput}
                    placeholder="Requirements"
                    onChange={handleDependencyOutput}
                />
            </div>
        </div>
    );
}

export default DependencyTracker;