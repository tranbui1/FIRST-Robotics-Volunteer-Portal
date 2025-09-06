import CustomDropDown from "./CustomDropDown";

/**
 * AgeDropDown
 * 
 * Renders a dropdown component specifically for selecting age.
 * Uses the CustomDropDown component internally with age options from 13 to 100.
 * 
 * Props:
 *  - data (object): Question data containing id and prompt.
 *  - completedQuestions (object): Tracks answered questions.
 *  - setCompletedQuestions (function): Updates completedQuestions state.
 *  - saveAnswer (function): Persists selected answer.
 *  - sessionId (string): Current questionnaire session identifier.
 * 
 * Usage:
 *  <AgeDropDown 
 *      data={questionData} 
 *      completedQuestions={completedQuestions} 
 *      setCompletedQuestions={setCompletedQuestions}
 *      saveAnswer={saveAnswer} 
 *      sessionId={sessionId} 
 *  />
 */
const AgeDropDown = ({ data, completedQuestions, setCompletedQuestions, saveAnswer, sessionId }) => {
    const ages = Array.from({ length: 88 }, (_, i) => i + 13); // Ages 13-100
    
    return <CustomDropDown 
        prompt={"Select your age"} 
        options={ages} 
        data={data}
        completedQuestions={completedQuestions} 
        setCompletedQuestions={setCompletedQuestions}
        saveAnswer={saveAnswer}
        sessionId={sessionId}
    />;
} 

export default AgeDropDown;
