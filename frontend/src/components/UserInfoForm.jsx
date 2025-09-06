import { addCompletedQuestion } from "../utils/questionnaireUtils";
import { useState, useEffect } from "react";

/**
 * UserInfoForm
 * 
 * Renders a form component to collect user"s personal information (name, email, zipcode).
 * Tracks form data, validates inputs, updates completedQuestions state,
 * and saves the answers to the backend/session.
 * 
 * Props:
 *  - data (object): Question data containing id and question/prompt.
 *  - completedQuestions (object): Tracks answered questions.
 *  - setCompletedQuestions (function): Updates completedQuestions state.
 *  - saveAnswer (function): Persists form data.
 *  - sessionId (string): Current questionnaire session identifier.
 */
const UserInfoForm = ({ data, completedQuestions, setCompletedQuestions, saveAnswer, sessionId }) => {
    // Form field states
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        zipcode: ""
    });

    // Validation error states
    const [errors, setErrors] = useState({
        name: "",
        email: "",
        zipcode: ""
    });

    // Form submission state
    const [isSubmitted, setIsSubmitted] = useState(false);

    /**
     * validateEmail
     * Basic email validation using regex
     * 
     * @param {string} email - Email to validate
     * @returns {boolean} - True if email is valid
     */
    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    /**
     * validateZipcode
     * Basic US zipcode validation (5 digits or 5+4 format)
     * 
     * @param {string} zipcode - Zipcode to validate
     * @returns {boolean} - True if zipcode is valid
     */
    const validateZipcode = (zipcode) => {
        const zipcodeRegex = /^\d{5}(-\d{4})?$/;
        return zipcodeRegex.test(zipcode);
    };

    /**
     * handleInputChange
     * Updates form data and clears related errors
     * 
     * @param {string} field - Field name to update
     * @param {string} value - New field value
     */
    const handleInputChange = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));

        // Clear error for this field when user starts typing
        if (errors[field]) {
            setErrors(prev => ({
                ...prev,
                [field]: ""
            }));
        }
    };

    /**
     * validateForm
     * Validates all form fields and sets error messages
     * 
     * @returns {boolean} - True if form is valid
     */
    const validateForm = () => {
        const newErrors = {};
        let isValid = true;

        // Validate name
        if (!formData.name.trim()) {
            newErrors.name = "Name is required";
            isValid = false;
        }

        // Validate email
        if (!formData.email.trim()) {
            newErrors.email = "Email is required";
            isValid = false;
        } else if (!validateEmail(formData.email)) {
            newErrors.email = "Please enter a valid email address";
            isValid = false;
        }

        // Validate zipcode
        if (!formData.zipcode.trim()) {
            newErrors.zipcode = "Zipcode is required";
            isValid = false;
        } else if (!validateZipcode(formData.zipcode)) {
            newErrors.zipcode = "Please enter a valid zipcode (e.g., 12345 or 12345-6789)";
            isValid = false;
        }

        setErrors(newErrors);
        return isValid;
    };

    /**
     * handleSubmit
     * Handles form submission:
     *  - Validates form data
     *  - Updates local state
     *  - Marks question as completed
     *  - Saves the answer
     * 
     * @param {Event} e - Form submit event
     */
    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (validateForm()) {
            setIsSubmitted(true);
            const answerData = {
                name: formData.name.trim(),
                email: formData.email.trim(),
                zipcode: formData.zipcode.trim()
            };
            
            addCompletedQuestion(setCompletedQuestions, data.id, [answerData]);
            saveAnswer(sessionId, data.id, answerData, data.question);
        }
    };

    /**
     * useEffect: Load existing form data
     * Pre-populates the form if question has been previously answered.
     */
    useEffect(() => {
        if (completedQuestions[data.id] && completedQuestions[data.id].length > 0) {
            const savedData = completedQuestions[data.id][0];
            if (typeof savedData === "object" && savedData.name) {
                setFormData({
                    name: savedData.name || "",
                    email: savedData.email || "",
                    zipcode: savedData.zipcode || ""
                });
                setIsSubmitted(true);
            }
        }
    }, [completedQuestions, data.id]);

    return (
        <div className="user-info-form">
            <form onSubmit={handleSubmit}>
                {/* Name Field */}
                <div className="form-group">
                    <label htmlFor={`name-${data.id}`}>
                        Full Name *
                    </label>
                    <input
                        type="text"
                        id={`name-${data.id}`}
                        value={formData.name}
                        onChange={(e) => handleInputChange("name", e.target.value)}
                        className={errors.name ? "error" : ""}
                        placeholder="Enter your full name"
                        disabled={isSubmitted}
                    />
                    {errors.name && <span className="error-message">{errors.name}</span>}
                </div>

                {/* Email Field */}
                <div className="form-group">
                    <label htmlFor={`email-${data.id}`}>
                        Email Address *
                    </label>
                    <input
                        type="email"
                        id={`email-${data.id}`}
                        value={formData.email}
                        onChange={(e) => handleInputChange("email", e.target.value)}
                        className={errors.email ? "error" : ""}
                        placeholder="Enter your email address"
                        disabled={isSubmitted}
                    />
                    {errors.email && <span className="error-message">{errors.email}</span>}
                </div>

                {/* Zipcode Field */}
                <div className="form-group">
                    <label htmlFor={`zipcode-${data.id}`}>
                        Zipcode *
                    </label>
                    <input
                        type="text"
                        id={`zipcode-${data.id}`}
                        value={formData.zipcode}
                        onChange={(e) => handleInputChange("zipcode", e.target.value)}
                        className={errors.zipcode ? "error" : ""}
                        placeholder="12345 or 12345-6789"
                        disabled={isSubmitted}
                    />
                    {errors.zipcode && <span className="error-message">{errors.zipcode}</span>}
                </div>

                {/* Submit Button */}
                {!isSubmitted ? (
                    <button type="submit" className="submit-button">
                        Continue
                    </button>
                ) : (
                    <div className="success-message">
                        ✓ Information saved successfully
                        <button 
                            type="button" 
                            className="edit-button"
                            onClick={() => setIsSubmitted(false)}
                        >
                            Edit
                        </button>
                    </div>
                )}
            </form>
        </div>
    );
};

export default UserInfoForm;