/**
 * dynamicFontSize
 * 
 * Adjusts the font size of a question element dynamically based on the length
 * of the question and the device/screen size. Splits long questions into two
 * lines for better readability on large screens.
 * 
 * Args:
 *  - data (object): Contains the question text in `data.question`.
 *  - document (Document): The DOM document object for selecting and updating elements.
 * 
 * Behavior:
 *  - Detects device type (small/regular/wider phones, tablets, desktops, landscape, long screens)
 *  - Calculates base font size and minimum font size depending on device
 *  - Scales font according to question length using a division factor
 *  - Inserts a `<br>` in long questions for readability if appropriate
 *  - Forces the calculated font size with `!important` to override CSS
 * 
 * Usage:
 *  import dynamicFontSize from './dynamicFontSize';
 *  
 *  dynamicFontSize({ question: "What is your age?" }, document);
 * 
 * Notes:
 *  - Only updates elements with the class `.question`.
 *  - Designed to handle questions with 15–20 words on large screens by splitting lines.
 */
const dynamicFontSize = (data, document) => {
    if (data) {
        const questionLen = data.question.length;
        const question = document.querySelector(".question");
        
        if (question) {
            const screenWidth = window.innerWidth;
            const screenHeight = window.innerHeight;
            
            // Enhanced device detection with better phone/tablet distinction
            const isLandscape = window.matchMedia("(orientation: landscape)").matches;
            
            /* ========== DEVICE DETECTION ========== */

            // 1. Small phones
            const isSmallPhone = screenWidth <= 385 && screenHeight <= 800;
            
            // 2. Regular phones
            const isRegularPhone = screenWidth <= 490 && screenHeight >= 800;
            
            // 3. Wider phones
            const isWiderPhone = screenWidth >= 491 && screenWidth <= 700 && screenHeight <= 800;

            // 4. Landscape phones
            const isLandscapePhone = isLandscape && 
                                   screenHeight <= 400 && 
                                   screenWidth >= 700 &&
                                   screenWidth <= 1040;
            
            // 6. Long tablets
            const isLongTablet = screenWidth >= 701 && screenWidth <= 1023 && screenHeight >= 1024;
            
            // 7. Regular tablets
            const isRegularTablet = screenWidth >= 481 && screenWidth <= 700 && screenHeight < 1024;
            
            // 8. Desktops
            const isDesktop = screenWidth >= 1024;

            // 9. Long screens
            const isLongScreen = screenWidth >= 1024 && screenHeight <= 650;
            
            let baseFontSize, minFontSize, divisionFactor;
            
            if (isSmallPhone) {
                baseFontSize = 12;
                minFontSize = 8;
                divisionFactor = 10;
            } else if (isWiderPhone) {
                baseFontSize = 9;
                minFontSize = 5.5;
                divisionFactor = 11;
            } else if (isRegularPhone) {
                baseFontSize = 13;
                minFontSize = 8;
                divisionFactor = 14;
            } else if (isLandscapePhone) {
                baseFontSize = 11;
                minFontSize = 6;
                divisionFactor = 15;
            } else if (isLongTablet) {
                baseFontSize = 9;
                minFontSize = 6;
                divisionFactor = 17;
            } else if (isRegularTablet) {
                baseFontSize = 11;
                minFontSize = 6.5;
                divisionFactor = 16;
            } else if (isLongScreen) {
                baseFontSize = 12.2;
                minFontSize = 7;
                divisionFactor = 10;
            } else if (isDesktop) {
                baseFontSize = 10;
                minFontSize = 6;
                divisionFactor = 15;
            } else {
                // Fallback for any edge cases
                baseFontSize = 10;
                minFontSize = 6;
                divisionFactor = 14;
            }
            
            const scaleFactor = Math.max(
                minFontSize, 
                baseFontSize - (questionLen / divisionFactor)
            );
            
            // Force override any CSS with !important
            question.style.setProperty('font-size', `${scaleFactor}vmin`, 'important');
            
            const words = data.question.split(' ');
            
            // Split up the sentence for better readability
            if (words.length >= 15 && words.length <= 20 && (isDesktop || isLandscapePhone)) {
                const midPoint = Math.ceil(words.length / 2);
                const connectingWords = ['with', 'and', 'or', 'but', 'the', 'a', 'an', 'of', 'in', 'on', 'at'];
                let breakPoint = midPoint;
                
                if (connectingWords.includes(words[breakPoint - 1]?.toLowerCase())) {
                    breakPoint++;
                }
                
                question.innerHTML = `${words.slice(0, breakPoint).join(' ')}<br>${words.slice(breakPoint).join(' ')}`;
            } else {
                question.textContent = data.question; 
            }
        }
    }
};

export default dynamicFontSize;