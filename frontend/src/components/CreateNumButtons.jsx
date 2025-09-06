import { useRef, useEffect, useState } from 'react';
import { addCompletedQuestion, removeCompletedQuestion } from '../utils/questionnaireUtils'

/**
 * CreateNumButtons
 * 
 * Renders a group of selectable numeric buttons for a questionnaire, tracks the selected option,
 * and updates the completed questions state as well as saving the answer.
 * 
 * Props:
 *  - data (object): Question data containing id, question text, and options array.
 *  - size (number): Button size modifier (1: default, 2: tall, 3: large).
 *  - completedQuestions (object): Tracks answered questions.
 *  - setCompletedQuestions (function): Updates completedQuestions state.
 *  - saveAnswer (function): Persists selected answer.
 *  - sessionId (string): Current questionnaire session identifier.
 */
const CreateNumButtons = ({ data, size, completedQuestions, setCompletedQuestions, saveAnswer, sessionId }) => {
    // CSS class for container based on button size
    const divClass = `button-container-${size}`;

    // Ref to container div (optional, e.g., for focus/scroll handling)
    const containerRef = useRef(null);

    // Tracks currently selected button's option key
    const [selectedButton, setSelectedButton] = useState(null);
             
    /**
     * handleButtonClick
     * 
     * Handles user click on a button:
     *  - Toggles selection (deselect if already selected)
     *  - Updates completedQuestions state
     *  - Saves answer to backend/session
     * 
     * @param {Event} event - Click event from button
     */
    const handleButtonClick = (event) => {
        const buttonId = event.target.id;
        const buttonText = event.target.textContent;
        const optionKey = data.options[parseInt(buttonId.replace('button', ''))]; // Get actual option key
        
        if (optionKey === selectedButton) {
            // Deselect button
            setSelectedButton(null);
            removeCompletedQuestion(completedQuestions, setCompletedQuestions, data.id);
        } else {
            // Select new button
            setSelectedButton(optionKey); 
            addCompletedQuestion(setCompletedQuestions, data.id, optionKey); 
            saveAnswer(sessionId, data.id, optionKey, data.question); 
        }
    }

    /**
     * Sync selected button with completedQuestions prop
     *  - Runs whenever completedQuestions or question id changes
     */
    useEffect(() => {
        if (completedQuestions[data.id]) {
            // Pre-select button if already answered
            setSelectedButton(completedQuestions[data.id][0]); 
        } else {
            setSelectedButton(null);
        }
    }, [completedQuestions, data.id]);

    return (
        <div ref={containerRef} className={`center ${divClass}`}>
            {data.options.map((option, index) => (
                <button 
                    key={index}
                    id={`button${index}`}
                    className={`questionnaire-button button-wide
                                ${selectedButton === option ? "selected-button" : ""}
                                ${size == 2 ? "button-tall" : ""}
                                ${size == 3 ? "button-large" : ""}
                                `}
                    onClick={handleButtonClick}
                >
                    {option}
                </button>
            ))}
        </div>
    );
}

export default CreateNumButtons;
