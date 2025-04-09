// Make functions available globally
window.startNavigation = startNavigation;
window.drawPath = drawPath;
window.displayRoute = displayRoute;

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    const navButton = document.getElementById('nav-button');
    if (navButton) {
        navButton.addEventListener('click', startNavigation);
    }
});

// Simulate WiFi scanning
function getWifiData() {
    return {
        rssi1: -65 + Math.random() * 5,
        rssi2: -70 + Math.random() * 5,
        rssi3: -68 + Math.random() * 5,
        rssi4: -75 + Math.random() * 5
    };
}

// Main navigation function
async function startNavigation() {
    const destination = document.getElementById('destination').value;
    const startLocation = document.getElementById('start-location').value;

    if (!startLocation || !destination) {
        alert('Please select both start location and destination');
        return;
    }

    try {
        const response = await fetch('/navigate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...getWifiData(),
                destination: destination,
                startLocation: startLocation // Add start location for future use
            })
        });

        const result = await response.json();
        console.log("Navigation Result:", result); // Log the entire result
        if (result.error) {
            alert(result.error);
            return;
        }
        displayRoute(result);
        drawPath(result.path);

    } catch (error) {
        console.error("Navigation error:", error);
        alert("Navigation error. Please try again.");
    }
}

// Display route information
function displayRoute(routeData) {
    const routeInfo = document.getElementById('route-info');
    routeInfo.innerHTML = `
        <h3>Navigation Info</h3>
        <p><strong>Current Position:</strong> ${routeData.current.join(', ')}</p>
        <p><strong>Distance:</strong> ${routeData.distance} units</p>
    `;
}

// Enhanced path drawing function
function drawPath(path) {
    const svg = document.getElementById('path-overlay');
    const mapImage = document.getElementById('map-image');
    svg.innerHTML = '';

    if (!path || path.length === 0) {
        alert("No path found!");
        return;
    }

    console.log("Path Data:", path); // Log the path data

    // Get the natural dimensions of the map image (from the file)
    const naturalWidth = 2000; // As per your description
    const naturalHeight = 2000; // As per your description
    const aspectRatio = naturalWidth / naturalHeight;

    // Get the displayed dimensions of the map image
    const displayedWidth = mapImage.offsetWidth;
    const displayedHeight = mapImage.offsetHeight;

    console.log("Displayed Width:", displayedWidth, "Displayed Height:", displayedHeight);

    // Calculate scaling factors, maintaining aspect ratio
    let scaleX = displayedWidth / 20;
    let scaleY = displayedHeight / 25;

    // Adjust scaling to fit within the displayed area
    const imageAspectRatio = displayedWidth / displayedHeight;
    const gridAspectRatio = 20 / 25;

    if (imageAspectRatio > gridAspectRatio) {
        scaleX = scaleY * gridAspectRatio / imageAspectRatio * (displayedWidth / 20 / (displayedHeight / 25));
        scaleX = displayedWidth / 20;
    } else {
        scaleY = scaleX * imageAspectRatio / gridAspectRatio * (displayedHeight / 25 / (displayedWidth / 20));
        scaleY = displayedHeight / 25;
    }


    console.log("Scale X:", scaleX, "Scale Y:", scaleY);

    // Set SVG dimensions to match the displayed image dimensions
    svg.setAttribute('width', displayedWidth);
    svg.setAttribute('height', displayedHeight);
    svg.style.position = 'absolute'; // Ensure it overlays correctly
    svg.style.top = '0';
    svg.style.left = '0';

    // Create path with improved visibility
    const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const dAttribute = path.map((p, i) => {
        const scaledX = p[0] * scaleX;
        const scaledY = p[1] * scaleY;
        console.log(`Point ${i}: Original [${p[0]}, ${p[1]}], Scaled [${scaledX}, ${scaledY}]`);
        return `${i === 0 ? 'M' : 'L'} ${scaledX} ${scaledY}`;
    }).join(' ');
    pathElement.setAttribute('d', dAttribute);
    pathElement.setAttribute('stroke', '#4285f4');
    pathElement.setAttribute('stroke-width', '8'); // Adjust as needed
    pathElement.setAttribute('fill', 'none');
    pathElement.setAttribute('stroke-linecap', 'round');
    pathElement.setAttribute('stroke-linejoin', 'round');
    svg.appendChild(pathElement);

    // Add start marker (blue circle)
    const startPoint = path[0];
    const startCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    startCircle.setAttribute('cx', startPoint[0] * scaleX);
    startCircle.setAttribute('cy', startPoint[1] * scaleY);
    startCircle.setAttribute('r', '10'); // Adjust as needed
    startCircle.setAttribute('fill', '#4285f4');
    svg.appendChild(startCircle);

    // Add destination marker (red circle)
    const endPoint = path[path.length - 1];
    const destinationMarker = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    destinationMarker.setAttribute('cx', endPoint[0] * scaleX);
    destinationMarker.setAttribute('cy', endPoint[1] * scaleY);
    destinationMarker.setAttribute('r', '10'); // Adjust as needed
    destinationMarker.setAttribute('fill', '#EA4335');
    svg.appendChild(destinationMarker);
}