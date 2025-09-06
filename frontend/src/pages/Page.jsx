import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import './Page.css';

/**
 * Page Component
 * --------------
 * Displays details for a specific role, including video introduction, express sign-up, 
 * and full description links. Fetches role-specific links from the backend API.
 *
 * Features:
 *  - Decodes URL parameters to get role name
 *  - Supports both YouTube and native video playback
 *  - Tracks whether the video has been played before showing action buttons
 *  - Handles errors and loading states
 * 
 * Note:
 *  - Lacks CSS.
 */
const Page = () => {
    const { roleName } = useParams(); // Extract role name from URL (/results/:roleName)
    const location = useLocation();    // Access location state passed from navigation
    const navigate = useNavigate();    // For programmatic navigation

    // State variables for links, video status, loading, and errors
    const [expressLink, setExpressLink] = useState(null); // Express sign-up link
    const [descLink, setDescLink] = useState(null);       // Full description link
    const [videoLink, setVideoLink] = useState(null);     // Video introduction link
    const [loading, setLoading] = useState(true);         // Loading state for API
    const [error, setError] = useState(null);             // Error message
    const [videoPlayed, setVideoPlayed] = useState(false);// Tracks if video has been played

    // Decode URL parameter to get the original role name
    const decodedRoleName = decodeURIComponent(roleName);
    
    // Optional roleName and allResults passed via state
    const roleNameFromState = location.state?.roleName;
    const allResults = location.state?.allResults;
    
    // Prefer roleName from state if available
    const actualRoleName = roleNameFromState || decodedRoleName;

    // Converts YouTube URL to embeddable format
    const getYouTubeEmbedUrl = (url) => {
        if (!url) return null;
        const patterns = [
            /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/,
            /youtube\.com\/embed\/([^&\n?#]+)/
        ];
        for (const pattern of patterns) {
            const match = url.match(pattern);
            if (match) return `https://www.youtube.com/embed/${match[1]}`;
        }
        return null;
    };

    // Checks if a URL is a YouTube link
    const isYouTubeUrl = (url) => {
        return url && (url.includes('youtube.com') || url.includes('youtu.be'));
    };

    // Fetch role-specific links from the backend
    const getRoleLinks = async (roleName) => {
        try {
            setLoading(true);   // Start loading
            setError(null);     // Reset error

            const response = await fetch("http://localhost:5001/api/role-links", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ "role_name": roleName })
            });

            if (!response.ok) {
                throw new Error(`HTTP error, status: ${response.status}`);
            }

            const result = await response.json();
            console.log('API response:', result);

            // Update state with returned links
            setExpressLink(result["express_link"]);
            setDescLink(result["desc_link"]);
            setVideoLink(result["video_link"]);
        } catch (error) {
            console.error("Failed to fetch role links", error);
            setError("Failed to load role links. Please try again.");
        } finally {
            setLoading(false);  // Stop loading
        }
    };

    // Fetch role links whenever the role name changes
    useEffect(() => {
        if (actualRoleName) getRoleLinks(actualRoleName);
    }, [actualRoleName]);

    // Mark video as played
    const handleVideoPlay = () => setVideoPlayed(true);

    // Open express sign-up link in a new tab
    const handleExpressSignUp = () => {
        if (expressLink) window.open(expressLink, '_blank', 'noopener,noreferrer');
        else alert('Express sign up link not available');
    };

    // Open full description link in a new tab
    const handleFullDescription = () => {
        if (descLink) window.open(descLink, '_blank', 'noopener,noreferrer');
        else alert('Full description link not available');
    };

    return (
        <div className="role-page">
            {/* Back navigation button */}
            <button onClick={() => navigate(-1)}>← Back</button>
            
            {/* Role title */}
            <h1>Role Details: {actualRoleName}</h1>
            
            <div>
                {/* Basic role description */}
                <p>Details for {actualRoleName} role...</p>

                {/* Optional: show full results passed via state */}
                {allResults && (
                    <div>
                        <h3>Full Results:</h3>
                        <pre>{JSON.stringify(allResults, null, 2)}</pre>
                    </div>
                )}
            </div>

            <br />

            {/* Video section */}
            <h2>Video Introduction</h2>
            {videoLink && !loading ? (
                <div className="video-container">
                    {isYouTubeUrl(videoLink) ? (
                        <iframe
                            className="video"
                            width="100%"
                            height="400"
                            src={getYouTubeEmbedUrl(videoLink)}
                            title="YouTube video player"
                            frameBorder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowFullScreen
                            onLoad={() => setVideoPlayed(true)} // Auto-show buttons for YouTube
                        />
                    ) : (
                        <video
                            controls
                            width="100%"
                            onPlay={handleVideoPlay} // Mark video as played
                            onError={(e) => console.error('Video error:', e)}
                        >
                            <source src={videoLink} type="video/mp4" />
                            <source src={videoLink} type="video/webm" />
                            <source src={videoLink} type="video/ogg" />
                            Your browser does not support the video tag.
                        </video>
                    )}
                </div>
            ) : (
                <p>Video not available - videoLink: {String(videoLink)}, loading: {String(loading)}</p>
            )}

            {/* Action buttons - shown only after video played */}
            {videoPlayed && (
                <div className="button-container">
                    <button onClick={handleExpressSignUp} disabled={loading || !expressLink}>
                        {loading ? 'Loading...' : 'Express Sign Up →'}
                    </button>
                    <button onClick={handleFullDescription} disabled={loading || !descLink}>
                        {loading ? 'Loading...' : 'Full Description →'}
                    </button>
                </div>
            )}

            {/* Display error if any */}
            {error && <p>{error}</p>}
        </div>
    );
};

export default Page;
