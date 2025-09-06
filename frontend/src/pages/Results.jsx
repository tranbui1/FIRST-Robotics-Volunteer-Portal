import { useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './Results.css';

/**
 * Results Component
 * -----------------
 * Displays the results of the user's assessment.
 * 
 * Features:
 *  - Loads results from navigation state or localStorage
 *  - Persists results in localStorage for 24 hours
 *  - Dynamically displays best-fit roles as clickable buttons
 *  - Handles proper URL encoding for role navigation
 * 
 * Note:
 *  - Lacks CSS.
 */
function Results() {
    const location = useLocation();   // Access navigation state
    const navigate = useNavigate();   // For programmatic navigation
    
    const [currentResults, setCurrentResults] = useState(null); // Loaded results
    const [options, setOptions] = useState([]);                // Best-fit roles

    // Load results from navigation or storage on mount
    useEffect(() => {
        const incomingResults = location.state?.results;
        
        if (incomingResults) {
            // Fresh results from navigation
            setCurrentResults(incomingResults);
            saveResultsToStorage(incomingResults);
            console.log("Fresh results loaded and saved");
        } else {
            // Try to load from storage if no fresh results
            const savedResults = loadResultsFromStorage();
            if (savedResults) {
                setCurrentResults(savedResults);
                console.log("Loaded results from storage");
            } else {
                console.log("No results found in state or storage");
            }
        }
    }, [location.state]);

    // Update button options when results change
    useEffect(() => {
        if (currentResults?.results?.["Best fit roles"]) {
            const newOptions = currentResults.results["Best fit roles"].trim().split(",") || [];
            setOptions(newOptions);
        } else {
            setOptions([]);
        }
    }, [currentResults]);

    // Save results to localStorage for persistence
    const saveResultsToStorage = (results) => {
        try {
            localStorage.setItem('assessmentResults', JSON.stringify(results));
            localStorage.setItem('resultsTimestamp', Date.now().toString());
        } catch (error) {
            console.error("Failed to save results to storage:", error);
        }
    };

    // Load results from localStorage if available and not expired
    const loadResultsFromStorage = () => {
        try {
            const savedResults = localStorage.getItem('assessmentResults');
            const timestamp = localStorage.getItem('resultsTimestamp');
            
            const MAX_AGE = 24 * 60 * 60 * 1000; // 24 hours in ms
            if (timestamp && Date.now() - parseInt(timestamp) > MAX_AGE) {
                console.log("Saved results are too old, clearing storage");
                clearResultsFromStorage();
                return null;
            }
            
            return savedResults ? JSON.parse(savedResults) : null;
        } catch (error) {
            console.error("Failed to load results from storage: ", error);
            return null;
        }
    };

    // Clear results from localStorage
    const clearResultsFromStorage = () => {
        try {
            localStorage.removeItem('assessmentResults');
            localStorage.removeItem('resultsTimestamp');
        } catch (error) {
            console.error("Failed to clear results from storage: ", error);
        }
    };

    // Navigate to role details page with proper URL encoding
    const dynamicButtonClick = (roleName) => {
        const cleanRoleName = roleName.trim();
        const encodedRoleName = encodeURIComponent(cleanRoleName); // Encode special characters
        
        console.log("Original role name:", cleanRoleName);
        console.log("Encoded role name:", encodedRoleName);
        
        navigate(`/results/${encodedRoleName}`, {
            state: {
                roleName: cleanRoleName,  // Preserve original name in state
                allResults: currentResults
            }
        });
    };

    // Show loading state if results are not yet available
    if (currentResults === null) {
        return (
            <div className="results">
                <div className="top-row">
                    <h2 className="header">Loading Results...</h2>
                </div>
            </div>
        );
    }

    return (
        <div className="results">
            {/* Header and result summary */}
            <div className="top-row">
                <h2 className="header">Assessment Results</h2>
                
                {currentResults ? (
                    <div className="info">
                        <p>Status: {currentResults.status}</p>
                        <p>Session ID: {currentResults.session_id}</p>
                        <br />
                        
                        {currentResults.results && (
                            <div>
                                <h3>Your Best Fit Roles:</h3>
                                <pre>{JSON.stringify(currentResults.results, null, 2)}</pre>
                            </div>
                        )}
                    </div>
                ) : (
                    <p>No results available</p>
                )}
            </div>

            {/* Buttons for top 3 best-fit roles */}
            <div className="button-container">
                {options.slice(0, 3).map((option, index) => (
                    <button 
                        key={index}
                        onClick={() => dynamicButtonClick(option)}
                    >
                        {option.trim()}
                    </button>
                ))}
            </div>
        </div>
    );
}

export default Results;
