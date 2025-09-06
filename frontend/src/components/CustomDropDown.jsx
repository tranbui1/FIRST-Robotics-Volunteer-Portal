import { addCompletedQuestion } from '../utils/questionnaireUtils'
import { useState, useEffect, useRef } from 'react';

/**
 * CustomDropDown
 * 
 * Renders a dropdown selection component for a questionnaire.
 * Tracks the selected option, updates completedQuestions state,
 * and saves the answer to the backend/session.
 * 
 * Props:
 *  - options (array, optional): Array of string options to display.
 *  - data (object): Question data containing id, question/prompt, and options array.
 *  - completedQuestions (object): Tracks answered questions.
 *  - setCompletedQuestions (function): Updates completedQuestions state.
 *  - saveAnswer (function): Persists selected answer.
 *  - sessionId (string): Current questionnaire session identifier.
 */
const CustomDropDown = ({ options, data, completedQuestions, setCompletedQuestions, saveAnswer, sessionId }) => {
    // Dropdown open/close state
    const [isOpen, setIsOpen] = useState(false);

    // Currently selected option
    const [choice, setChoice] = useState(null);

    // Ref for detecting clicks outside the dropdown
    const dropdownRef = useRef(null);
    const buttonRef = useRef(null);

    /**
     * useEffect: Detect clicks outside of dropdown
     * Closes the dropdown when user clicks anywhere outside.
     */
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    /**
     * handleChoice
     * 
     * Handles user selecting an option:
     *  - Updates local selected choice state
     *  - Closes dropdown
     *  - Marks question as completed
     *  - Saves the answer
     * 
     * @param {string} option - Selected dropdown option
     */
    const handleChoice = (option) => {
        setChoice(option);
        setIsOpen(false);
        addCompletedQuestion(setCompletedQuestions, data.id, option);
        saveAnswer(sessionId, data.id, option, data.question);
    };

    /**
     * useEffect: Load existing selection
     *  - Pre-populates the dropdown if question has been previously answered.
     */
    useEffect(() => {
        if (completedQuestions[data.id] && completedQuestions[data.id].length > 0) {
            setChoice(completedQuestions[data.id][0]);
        }
    }, [completedQuestions, data.id]);

    return (
        <div className="custom-dropdown" ref={dropdownRef}>
            <button ref={buttonRef} onClick={() => setIsOpen(!isOpen)} aria-expanded={isOpen}> 
                <span className="custom-dropdown-text">{choice || data.prompt}</span>
                <span className="arrow">▼</span>
            </button>
            {isOpen && (
                <ul>
                    {(options || data.options).map(option => (
                        <li key={option} onClick={() => handleChoice(option)}>
                            {option}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
} 

export default CustomDropDown;
