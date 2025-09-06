import './Home.css';
import { useNavigate } from 'react-router-dom';

/**
 * Home Component
 * --------------
 * Landing page for FIRST Robotics volunteers.
 * Provides an introduction and a button to start the matching questionnaire.
 *
 * Behavior:
 *  - Displays a title and a short description.
 *  - Clicking the "Match me to a role!" button navigates the user to the /match route.
 * 
 * Note:
 *  - Simple placeholder for actual integration page.
 */
function Home() {
    const navigate = useNavigate(); // Hook to programmatically navigate between routes

    // Handle click on the button to navigate to the match page
    const handleClick = () => {
        navigate('/match'); // Redirects to the questionnaire/match page
    }

    return (
        <div>
            {/* Page title */}
            <h1> FIRST Robotics Volunteer Page </h1>

            <div className="center">
                {/* Description text */}
                <p className="home-description">
                    Interested in volunteering but don't know where to start? <br />
                    Take our matching questionnaire to find out the most <br />
                    suitable roles for you! :)
                </p>

                {/* Button to start the matching questionnaire */}
                <button 
                    className="button" 
                    type="button" 
                    onClick={handleClick}
                > 
                    Match me to a role! 
                </button>
            </div>
        </div>
    )
}

export default Home;
