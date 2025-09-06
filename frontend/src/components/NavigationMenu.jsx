/**
 * NavigationMenu Component
 * ------------------------
 * Provides navigation controls for the questionnaire.
 * 
 * Props:
 *  - handleNextAnswerClick (function): Advances to the next question(s)
 *  - handleBackAnswerClick (function): Goes back to previous question(s)
 *  - skipPhysicalQuestions (boolean): Whether to skip certain questions
 *  - handleSubmit (function): Submits the questionnaire
 *  - isModalOpen (boolean): Disables navigation if modal is open
 *  - questionId (number): Current question index (0-based)
 *  - completedRate (number): Progress completion rate (0-1)
 *
 * Behavior:
 *  - "Next" skips extra questions if skipPhysicalQuestions flag is true
 *  - "Back" skips extra questions if skipPhysicalQuestions flag is true
 *  - "Submit" only appears on the last question and if completion rate >= 99.9%
 */
const NavigationMenu = ({
    handleNextAnswerClick, 
    handleBackAnswerClick, 
    skipPhysicalQuestions,
    handleSubmit,          
    isModalOpen,           
    questionId,            
    completedRate          
}) => {

    const totalQuestions = 12; // Total number of questions

    // Handle "Next" button click 
    const handleNextClick = () => {
        if (questionId === 1 && skipPhysicalQuestions) {
            // Skip 2 questions forward if the condition is met
            handleNextAnswerClick(3);
        } else {
            // Normal next (skip 1 question)
            handleNextAnswerClick(1);
        }
    };

    // Handle "Back" button click
    const handleBackClick = () => {
        if (questionId === 4 && skipPhysicalQuestions) {
            // Skip back 2 questions if the condition is met
            handleBackAnswerClick(3);
        } else {
            // Normal back (skip 1 question)
            handleBackAnswerClick(1);
        }
    };

    return (
        <div className={`navigation ${isModalOpen ? "disabled" : ""}`}>
            {/* Show "Next" button if not at the last question */}
            {questionId < totalQuestions - 1 && (
                <h2
                    className="navigation-button"
                    onClick={handleNextClick}>
                    Next →
                </h2>
            )}

            {/* Show "Submit" button only on last question and if completion rate is >= 99.9% */}
            {questionId === totalQuestions - 1 && completedRate >= 0.999 && (
                <h2
                    className="navigation-button submit"
                    onClick={handleSubmit}>
                    Submit
                </h2>
            )}

            {/* Show "Back" button if not at the first question */}
            {questionId > 0 && (
                <h2
                    className="navigation-button"
                    onClick={handleBackClick}>
                    ← Back
                </h2>
            )}
        </div>
    );
}

export default NavigationMenu;
