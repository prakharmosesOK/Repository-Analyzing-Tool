import { useState, useEffect } from 'react';
import '../styles/DocGenerator.css';
import axios from 'axios';

const DocGenerator = () => {
    // Declare state variables
    const [searchItem, setSearchItem] = useState('');
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [filesInRepo, setFilesInRepo] = useState([]);
    // const [filesToGenerateDoc, setFilesToGenerateDoc] = useState([]);

    // Handle form submission
    const handleDocGeneratorSubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const response = await axios.post('http://127.0.0.1:8000/repoanalyze/get_files_from_repository/', {
                input: searchItem
            })
            const data = response.data.output;
            console.log(data);
            console.log("Files in Repo: ");
            setFilesInRepo(data)
            console.log(filesInRepo);
        } catch (error) {
            console.error('Error fetching files:', error);
            setError('Failed to retrieve files. Please try again later.');
        } finally {
            setIsLoading(false);
        }
    }

    // const fetchFilesFromDir = async (dir) => {
    //     dir.preventDefault();

    //     try {
    //         const response = await axios.post('http://127.0.0.1:8000/repoanalyze/get_files_from_dir/', {
    //             input: dir
    //         })
    //         const data = response.data.output;
    //         filesInRepo[dir] = data;
    //     } catch (error) {
    //         console.error('Error fetching files:', error);
    //         setError('Failed to retrieve files. Please try again later.');
    //     }
    // }

    // useEffect(() => {
    //     const displayFiles = () => {
    //         return (
    //             <div className="doc-generation">
    //                 <div className="files-container">
    //                     {filesInRepo && filesInRepo.map((file, index) => (
    //                         <input type='radio' key={index}>{file}</input>
    //                     ))}
    //                 </div>
    //                 {/* <button onClick={generateDocumentation}>Generate Doc</button> */}
    //             </div>
    //         )
    //     }
    //     displayFiles();
    // }, [filesInRepo])

    return (
        <div className="doc-generator-container">
            <form onSubmit={handleDocGeneratorSubmit}>
                <input
                    type="text"
                    value={searchItem}
                    onChange={(event) => setSearchItem(event.target.value)}
                    placeholder="Enter the GitHub repository link here for doc generation"
                />
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Loading...' : 'Fetch Repository'}
                </button>
            </form>

            {filesInRepo.length > 0 ? (
                <form>
                    {filesInRepo.map((file, index) => (
                        <div className="div">
                            <input
                                key={index}
                                type='checkbox'
                                name={file}
                            />
                            <label htmlFor={file}>{file}</label>
                        </div>
                    ))}
                    <button>Generate Doc</button>
                </form>) : null
            }

            {error && <p className="error-message">{error}</p>}


        </div>
    )
}

export default DocGenerator;