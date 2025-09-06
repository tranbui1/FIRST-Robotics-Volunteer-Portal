/**
 * questionnaireUtils.js
 * ---------------------
 * Helper functions for managing completed questions in the questionnaire state.
 * 
 * Features:
 *  - addCompletedQuestion: Add a single-answer question to completedQuestions
 *  - setCompletedQuestionsMulti: Replace answers for multi-select questions
 *  - removeCompletedQuestion: Remove a question from completedQuestions
 */

/**
 * Adds a single-answer question to the completedQuestions state.
 * @param {Function} setCompletedQuestions - React state setter for completedQuestions
 * @param {string|number} id - Question ID
 * @param {string} answer - User's answer
 */
const addCompletedQuestion = (setCompletedQuestions, id, answer) => {
    setCompletedQuestions(prev => ({        
        ...prev,           // Keep existing completed questions
        [id]: [answer]     // Add/update current question with a single answer
    }));
}

/**
 * Sets the completed answers for a multi-select question.
 * Replaces any previous answers for this question.
 * @param {Function} setCompletedQuestionsFunc - React state setter for completedQuestions
 * @param {string|number} id - Question ID
 * @param {Array} answersArray - Array of selected answers
 */
const setCompletedQuestionsMulti = (setCompletedQuestionsFunc, id, answersArray) => {
    setCompletedQuestionsFunc(prev => ({        
        ...prev,           // Keep existing completed questions
        [id]: answersArray // Replace answers for this multi-select question
    }));
}

/**
 * Removes a question from completedQuestions.
 * @param {Object} completedQuestions - Current completedQuestions state
 * @param {Function} setCompletedQuestions - React state setter for completedQuestions
 * @param {string|number} id - Question ID to remove
 */
const removeCompletedQuestion = (completedQuestions, setCompletedQuestions, id) => {
    if (id in completedQuestions) {
        setCompletedQuestions(prev => {
            const newObj = { ...prev }; // Create shallow copy
            delete newObj[id];          // Remove the question
            return newObj;              // Update state
        });
    }
}

export { addCompletedQuestion, setCompletedQuestionsMulti, removeCompletedQuestion };
