import { useState, useEffect } from 'react';
import axios from 'axios';

// Importing styles
import '../styles/DocumentationGen.css';

const DocumentationGen = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [zipFile, setZipFile] = useState(null);
    const [isDownloading, setIsDownloading] = useState(false);
    const [isDownloaded, setIsDownloaded] = useState(false);

    const handleDocGeneration = async (event) => {
        event.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const response = await axios.post('http://127.0.0.1:8000/repoanalyze/genDocument_from_docstr/', {
                input: searchTerm
            })
            const data = response.data.output;
            if (response.status === 200) {
                setZipFile(data);
                setError(null);
            } else {
                setError('Failed to generate documentation. Please try again later!');
                setZipFile(null);
            }
        } catch (error) {
            setError('Failed to generate documentation. Please try again later!');
            setZipFile(null);
        } finally {
            setIsLoading(false);
        }
    }

    const downloadDocumentation = async () => {
        console.log("Startinfg download!!");
        setIsDownloading(true);
        setIsDownloaded(false);
        setError(null);
        
        try {
            const response = await axios.post('http://127.0.0.1:8000/repoanalyze/download_documentation/', {
                    input: zipFile
                }, {
                responseType: 'blob'
            })
            const blob = response.data;
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'documentation.zip');
            link.click();
        } catch (error) {
            setError('Failed to download the documentatoin. Please try again later!');
        } finally {
            setIsDownloading(false);
            setIsDownloaded(true);
        }
    }

    useEffect(() => {
        const removeFromBackend = async () => {
            if (zipFile && isDownloaded) {
                try {
                    const response = await axios.post('http://127.0.0.1:8000/repoanalyze/remove_zip/', {
                        input: zipFile
                    })
                    if (response.status === 200) {
                        console.log(`Zip file removed from backend: ${zipFile}`);
                    }
                } catch (error) {
                    console.log(`Error while removing zip file: ${error}`);
                }
            }
        }

        removeFromBackend();
    }, [isDownloaded, zipFile])

    return (
        <main className='documentation-gen-container'>
            <form onSubmit={handleDocGeneration}>
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                    placeholder='Enter the repo url to generate documentation'
                />
                <button disabled={isLoading}>{isLoading ? 'Loading...' : "Generate Documentation"}</button>
            </form>

            {zipFile &&
                <button onClick={downloadDocumentation} disabled={isDownloading}>{isDownloading ? "Downloading..." : "Download Documentation"}</button>
            }

            {error && <p className='error-message'>{error}</p>}
        </main>
    );
}

export default DocumentationGen;