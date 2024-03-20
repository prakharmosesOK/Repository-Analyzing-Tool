import React, { useState, useRef } from 'react';
import '../styles/CommitHistory.css';
import axios from 'axios';

const CommitHistory = () => {
  const [searchItem, setSearchItem] = useState('');
  const [isLoading, setIsLoading] = useState(false); // Track loading state
  const [commitHistory, setCommitHistory] = useState([]); // Use singular form for clarity
  const [error, setError] = useState(null); // Handle potential errors

  const handleSearchTextChange = (event) => {
    setSearchItem(event.target.value);
  };

  const handleCommitSearchSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true); // Set loading state to indicate ongoing request
    setError(null); // Clear any previous errors

    try {
      const response = await axios.post('http://127.0.0.1:8000/repoanalyze/get_commit_history/', {
        input: searchItem,
      });

    //   setRequestText(response.data.output); // (Optional) Store full response if needed
      const data = response.data.output.split('$');
      console.log("Trying to print the data as follows: ");
      console.log(data);
      setCommitHistory(data);
    } catch (error) {
      console.error('Error fetching commit history:', error);
      setError('Failed to retrieve commit history. Please try again later.');
    } finally {
      setIsLoading(false); // Always reset loading state after request completes
    }
  };

  return (
    <div className="CommitHistoryContainer">
      <form onSubmit={handleCommitSearchSubmit}>
        <input
          type="text"
          value={searchItem}
          onChange={handleSearchTextChange}
          placeholder="Enter the GitHub repository link here"
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Submit'}
        </button>
      </form>

      {error && <p className="error-message">{error}</p>}

      {commitHistory.length > 0 && (
        <div className="commitoutput">
          {commitHistory.map((item, index) => (
            <div key={index} className="commitHistoryBlock">
              <p>{item}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CommitHistory;
