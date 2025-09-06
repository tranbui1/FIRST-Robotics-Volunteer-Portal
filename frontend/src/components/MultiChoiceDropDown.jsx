import { setCompletedQuestionsMulti, removeCompletedQuestion } from '../utils/questionnaireUtils'
import { useState, useEffect, useRef } from 'react';

/**
 * MultiChoiceDropDown
 * 
 * A dropdown component that allows multiple selections from a list of options.
 * Selected items are displayed above the dropdown and can be removed individually.
 * Updates completed questions state and saves answers to the backend.
 * 
 * Props:
 *  - data: object — Contains `id`, `prompt`, and `options` for the question.
 *  - completedQuestions: object — Tracks answers that have already been completed.
 *  - setCompletedQuestions: function — Setter to update completedQuestions state.
 *  - saveAnswer: function — Callback to save the selected answer(s) to the backend.
 *  - sessionId: string — Session identifier for saving answers.
 * 
 * Usage:
 *  <MultiChoiceDropDown
 *      data={questionData}
 *      completedQuestions={completedQuestions}
 *      setCompletedQuestions={setCompletedQuestions}
 *      saveAnswer={saveAnswer}
 *      sessionId={sessionId}
 *  />
 */

const MultiChoiceDropDown = ({ data, completedQuestions, setCompletedQuestions, saveAnswer, sessionId }) => {
    const [isOpen, setIsOpen] = useState(false); // Track dropdown open/close state
    const [choice, setChoice] = useState([]); // Track selected options
    const buttonRef = useRef(null); // Ref to the dropdown button
    const dropDownRef = useRef(null); // Ref to the dropdown container

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropDownRef.current && !dropDownRef.current.contains(event.target)) {
                setIsOpen(false); // Close dropdown
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    // Update completed questions and save answer whenever selection changes
    useEffect(() => {
        if (choice.length === 0) {
            removeCompletedQuestion(completedQuestions, setCompletedQuestions, data.id); // Remove if nothing selected
        } else {
            setCompletedQuestionsMulti(setCompletedQuestions, data.id, choice, data.question); // Update state
            const answerString = choice.join(", "); // Convert array to comma-separated string
            saveAnswer(sessionId, data.id, answerString, data.question); // Save answer
        }
    }, [choice]);

    // Load previous answers from completedQuestions when component mounts or updates
    useEffect(() => {
        if (completedQuestions[data.id]) {
            setChoice(completedQuestions[data.id]); // Pre-fill choices
        }
    }, [completedQuestions, data.id]);

    // Remove an individual choice when its "×" is clicked
    const handleRemoveOnClick = (event) => {
        event.stopPropagation(); // Prevent dropdown toggle
        const clickedItem = event.target;
        const clickedItemText = clickedItem.textContent.replace(/\s*×\s*$/, '').trim();
        setChoice(choice.filter((item) => item !== clickedItemText)); // Remove from state
    }

    return (
        <div className="custom-dropdown" ref={dropDownRef}>
            <button onClick={() => setIsOpen(!isOpen)} aria-expanded={isOpen} ref={buttonRef}>
                <span className="custom-dropdown-text">
                    {choice.length === 0 ? data.prompt : ""} {/* Show prompt if nothing selected */}
                </span>
                <div className={`selected-container ${choice.length === 1 ? 'single-item' : ''}`}>
                    {choice.length > 0
                        ? choice.map(item => (
                            <span 
                                key={item} 
                                onClick={(event) => { handleRemoveOnClick(event); setIsOpen(false); }} 
                                className="selected"
                            >
                                {`${item}  ×`} {/* Display selected option with remove button */}
                            </span>
                        ))
                        : ""}
                </div>
                <span className="arrow">▼</span> {/* Dropdown arrow */}
            </button>
            {isOpen && (
                <ul>
                    {data.options.map(option => (
                        <li 
                            className={`multi-choice ${choice.includes(option) ? 'delete' : ''}`} // Highlight if selected
                            key={option}
                            onClick={() => { setChoice(prev => [...prev, option]) }} // Add option to choice array
                        >
                            {option}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default MultiChoiceDropDown;

