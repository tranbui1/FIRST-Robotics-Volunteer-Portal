import './Questionnaire.css';
import { useState, useEffect } from 'react';
import RenderContent from '../components/RenderContent';
import Modal from '../components/Modal';
import NavigationMenu from '../components/NavigationMenu';
import dynamicFontSize from '../components/DynamicFontSize';
import { useNavigate } from 'react-router-dom';

/**
 * Questionnaire Component
 * -----------------------
 * Handles the interactive assessment questionnaire.
 * 
 * Features:
 *  - Starts a session on mount and stores session ID
 *  - Fetches questions from backend as user navigates
 *  - Dynamically renders question input types
 *  - Shows descriptions directly from question data
 *  - Tracks completed questions and progress
 *  - Saves answers to backend (auto-save)
 *  - Skips specific questions conditionally
 *  - Applies dynamic font sizing for question text
 *  - Handles exit modal and navigation
 */
function Questionnaire() {
    const [questionId, setQuestionId] = useState(0);          // Current question index
    const [data, setData] = useState(null);                   // Current question data
    const [isModalOpen, setModalOpen] = useState(false);      // Modal open state
    const [completedQuestions, setCompletedQuestions] = useState({}); // Answers saved locally
    const [sessionId, setSessionId] = useState(null);         // Backend session ID
    const [error, setError] = useState(null);                 // Error message
    const [skipPhysicalQuestions, setSkipPhysicalQuestions] = useState(null); // Conditional skip flag
    const [totalQuestions, setTotalQuestions] = useState(11); // Total number of questions

    const navigate = useNavigate();

    // Start a new session on component mount
    const startSession = async () => {
        try {
            const response = await fetch("http://localhost:5001/api/start-session", {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });

            if (!response.ok) throw new Error(`HTTP error, status: ${response.status}`);

            const result = await response.json();
            setSessionId(result.session_id);
            console.log("Session started:", result.session_id);

        } catch (error) {
            console.error("Failed to start session:", error);
            setError("Failed to start assessment session");
        }
    };
    
    // Fetch question data from backend
    const fetchData = async () => {
        try {
            const response = await fetch("http://localhost:5001/api/get-question", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ "question_id": questionId })
            });

            if (!response.ok) throw new Error(`HTTP error, status: ${response.status}`);

            const result = await response.json();
            setData(result);
        } catch (error) {
            console.error("Failed to fetch question data", error);
            setError("Failed to fetch question data");
        }
    };
    
    // Save answer to backend (auto-save)
    const saveAnswer = async (sessionId, questionId, answer, question, autoSave = true) => {
        try {
            if (autoSave && sessionId) {
                const response = await fetch("http://localhost:5001/api/save-answer", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ session_id: sessionId, question_id: questionId, answer, question })
                });

                if (!response.ok) throw new Error(`HTTP error, status: ${response.status}`);

                const result = await response.json();

                // Conditional skip logic for specific questions
                if (questionId === 1) {
                    if (result.skip) {
                        setSkipPhysicalQuestions(true);
                        setTotalQuestions(10); // Reduce total questions
                        console.log("Specific physical ability questions skipped")
                    } else {
                        setSkipPhysicalQuestions(false);
                        setTotalQuestions(12);
                    }
                }

                console.log(`Answer saved for question ${questionId}`);
            }
        } catch (error) {
            console.error("Failed to save answer", error);
            setError('Failed to save answer - your progress may not be saved');
            setTimeout(() => setError(null), 300); // Clear temporary error
        }
    };

    // Calculate completion rate
    const completedRate = totalQuestions > 0 
        ? Object.keys(completedQuestions).length / totalQuestions 
        : 0;

    // Navigate to next question
    const handleNextAnswerClick = (numSkips = 1) => {
        setQuestionId(prev => prev + numSkips); 
    };

    // Navigate to previous question
    const handleBackAnswerClick = (numSkips = 1) => {
        setQuestionId(prev => prev - numSkips); 
    };

    // Submit the questionnaire
    const handleSubmit = async () => {
        if (!sessionId) {
            alert("No active session found. Please refresh and try again.");
            return;
        }

        try {
            const response = await fetch("http://localhost:5001/api/submit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId })
            });

            if (!response.ok) throw new Error(`HTTP error, status: ${response.status}`);

            const result = await response.json();
            navigate("/results", { state: { results: result } });
            
        } catch (error) {
            console.error('Failed to submit assessment:', error);
            alert('Failed to submit assessment. Please try again.');
        }
    };

    // Start session on mount
    useEffect(() => { startSession(); }, []);

    // Fetch new question whenever questionId changes
    useEffect(() => { fetchData(); }, [questionId]);

    // Apply dynamic font sizing when question data updates
    useEffect(() => { dynamicFontSize(data, document); }, [data]);

    return (
        <div id="disable-copy" className="flat background" style={{backgroundImage: 'url(/images/background.jpg)'}}>
            {/* Progress bar */}
            <div><progress value={completedRate} max="1"/></div>

            {/* Header with exit button and logo */}
            <div className="header">
                <p className="exit" onClick={() => setModalOpen(true)}> × Exit</p>
                <img className="logo" src="/images/logo.png" alt="FIRST Robotics logo" />
            </div>

            {/* Question text */}
            <h1 className="center question">{data ? data.question : 'Loading...'}</h1>

            {/* Question-specific description from data */}
            {data && data.description && (
                <div className="description">
                    <p>{data.description}</p>
                </div>
            )}

            {/* Dynamic input based on question type */}
            <div className="input-container">
                {data ? (
                    <RenderContent 
                        data={data} 
                        completedQuestions={completedQuestions}
                        setCompletedQuestions={setCompletedQuestions}
                        sessionId={sessionId}
                        saveAnswer={saveAnswer}
                    /> 
                ) : "Loading"}
            </div>

            {/* Error message display */}
            {error && (
                <div className="error-message">
                    <p>{error}</p>
                </div>
            )}

            {/* Exit confirmation modal */}
            {isModalOpen && <Modal setModalOpen={setModalOpen}/>}

            {/* Navigation menu for next/back/submit */}
            <NavigationMenu 
                handleNextAnswerClick={handleNextAnswerClick}
                handleBackAnswerClick={handleBackAnswerClick}
                skipPhysicalQuestions={skipPhysicalQuestions}
                handleSubmit={handleSubmit}
                isModalOpen={isModalOpen}
                questionId={questionId}
                completedRate={completedRate}
            />   
        </div>
    );
}

export default Questionnaire;