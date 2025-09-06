import CreateNumButtons from './CreateNumButtons';
import AgeDropDown from './AgeDropDown';
import CustomDropDown from './CustomDropDown';
import MultiChoiceDropDown from './MultiChoiceDropDown';
import UserInfoForm from './UserInfoForm'; // Add this import

/**
 * RenderContent Component
 * -----------------------
 * Dynamically renders the appropriate input component based on the question type.
 *
 * Props:
 *  - data (object): Contains question details including `id`, `type`, `question`, `options`, etc.
 *  - completedQuestions (object): Tracks user-selected answers keyed by question id.
 *  - setCompletedQuestions (function): Updates the completedQuestions state.
 *  - saveAnswer (function): Saves the user's answer to the backend or session.
 *  - sessionId (string): Unique session identifier for the user.
 *
 * Behavior:
 *  - Renders different components such as AgeDropDown, CreateNumButtons, MultiChoiceDropDown, 
 *    CustomDropDown, or UserInfoForm depending on the `data.type` of the question.
 */
const RenderContent = ({ data, completedQuestions, setCompletedQuestions, saveAnswer, sessionId }) => {
    // Switch based on the type of question
    switch (data.type) {
        
        case "number-age":
            // Age selection dropdown
            return <AgeDropDown
                key={data.id} 
                data={data}
                completedQuestions={completedQuestions} 
                setCompletedQuestions={setCompletedQuestions}
                saveAnswer={saveAnswer}
                sessionId={sessionId}
            />;

        case "select-2":
            // 2-choice number buttons
            return <CreateNumButtons 
                key={data.id}
                data={data}
                size={2} // 2 options per row
                completedQuestions={completedQuestions} 
                setCompletedQuestions={setCompletedQuestions}
                saveAnswer={saveAnswer}
                sessionId={sessionId}
            />;

        case "select-3":
            // 3-choice number buttons
            return <CreateNumButtons 
                key={data.id}
                data={data} 
                size={3} // 3 options per row
                completedQuestions={completedQuestions} 
                setCompletedQuestions={setCompletedQuestions}
                saveAnswer={saveAnswer}
                sessionId={sessionId}
            />;

        case "multiselect":
            // Multi-select dropdown
            return <MultiChoiceDropDown
                key={data.id} 
                data={data}
                completedQuestions={completedQuestions} 
                setCompletedQuestions={setCompletedQuestions}
                saveAnswer={saveAnswer}
                sessionId={sessionId}
            />;

        case "custom-dropdown":
            // Generic single-select dropdown
            return <CustomDropDown 
                key={data.id}
                data={data}
                completedQuestions={completedQuestions} 
                setCompletedQuestions={setCompletedQuestions}
                saveAnswer={saveAnswer}
                sessionId={sessionId}
            />;

        case "user-info":
            // User information form (name, email, zipcode)
            return <UserInfoForm
                key={data.id}
                data={data}
                completedQuestions={completedQuestions}
                setCompletedQuestions={setCompletedQuestions}
                saveAnswer={saveAnswer}
                sessionId={sessionId}
            />;

        default:
            return null; // Fallback for unknown question types
    }
}

export default RenderContent;