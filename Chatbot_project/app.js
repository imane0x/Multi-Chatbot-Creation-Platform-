
// Get the button element by ID
const autobotCreateBtn = document.getElementById('autobotCreateBtn');

// Add event listener to handle the click event
autobotCreateBtn.addEventListener('click', function() {
  // Perform the desired action, e.g., show an alert
  alert('Create New Bot button clicked!');
  
  // Alternatively, you can perform other actions such as redirecting to a new page
  window.location.href = '/menu';
});


// Get the button element by ID
const submit_menu = document.getElementById('submit_button');

// Add event listener to handle the click event
autobotCreateBtn.addEventListener('click', function() {
  // Perform the desired action, e.g., show an alert
  alert('Create New Bot button clicked!');
  
  // Alternatively, you can perform other actions such as redirecting to a new page
  window.location.href = '/bot';
});

personalityDropdown.addEventListener('change', function() {
    const selectedPersonality = personalityDropdown.value;
    console.log(`Selected Personality: ${selectedPersonality}`); // Log the selected value

    fetch('/update-personality', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ personality: selectedPersonality })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Personality updated successfully:', data);
    })
    .catch(error => {
        console.error('Error updating personality:', error);
    });
});

const fileInput = document.getElementById('file-upload');
fileInput.addEventListener('change', function() {
    const files = fileInput.files;
    for (let i = 0; i < files.length; i++) {
        if (files[i].size > 5 * 1024 * 1024) { // 5MB in bytes
            alert('File ' + files[i].name + ' is too large. Maximum size is 5MB.');
            fileInput.value = ''; // Clear the input
            break;
        }
    }
});