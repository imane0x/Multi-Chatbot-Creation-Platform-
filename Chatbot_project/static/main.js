function getCurrentTimestamp() {
	return new Date();
}

/**
 * Renders a message on the chat screen based on the given arguments.
 * This is called from the `showUserMessage` and `showBotMessage`.
 */
function renderMessageToScreen(args) {
	// local variables
	let displayDate = (args.time || getCurrentTimestamp()).toLocaleString('en-IN', {
		month: 'short',
		day: 'numeric',
		hour: 'numeric',
		minute: 'numeric',
	});
	let messagesContainer = $('.messages');

	// init element
	let message = $(` 
	<li class="message ${args.message_side}">
		<div class="avatar"></div>
		<div class="text_wrapper">
			<div class="text">${args.text}</div>
			<div class="timestamp">${displayDate}</div>
		</div>
	</li>
	`);

	// add to parent
	messagesContainer.append(message);

	// animations
	setTimeout(function () {
		message.addClass('appeared');
	}, 0);
	messagesContainer.animate({ scrollTop: messagesContainer.prop('scrollHeight') }, 300);
}

/**
 * Displays the user message on the chat screen. This is the right side message.
 */
function showUserMessage(message, datetime) {
	renderMessageToScreen({
		text: message,
		time: datetime,
		message_side: 'right',
	});
}

/**
 * Displays the chatbot message on the chat screen. This is the left side message.
 */
function showBotMessage(message, datetime) {
	renderMessageToScreen({
		text: message,
		time: datetime,
		message_side: 'left',
	});
}

/**
 * Sends a message when the 'Enter' key is pressed.
 */
$(document).ready(function() {
	$('#msg_input').keydown(function(e) {
		// Check for 'Enter' key
		if (e.key === 'Enter') {
			// Prevent default behaviour of enter key
			e.preventDefault();
			// Trigger send button click event
			$('#send_button').click();
		}
	});
});

/**
 * Handle sending the user message and getting the bot response.
 */
// 
$('#send_button').on('click', function (e) {
    const textField = $('#msg_input');
    const userMessage = textField.val();

    if (userMessage === "") return; // Do nothing if the input is empty

    // Get selected personality from dropdown
    const selectedPersonality = $('#chatbot-personality').val();

    // Display user message
    showUserMessage(userMessage);

    // Send user message and personality to the server
    fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        body: JSON.stringify({
            // personality: selectedPersonality, // Include personality in the payload
            contents: [
                {
                    parts: [
                        { text: userMessage },
						{personality :  selectedPersonality}
                    ]
                }
            ]
        }),
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Check if the bot response is available
        if (data.answer) {
            showBotMessage(data.answer); // Display the bot's answer
        } else {
            showBotMessage("Sorry, I couldn't understand that."); // Default message if no response
        }
        // Clear the input field and reset
        textField.val('');
    })
    .catch(error => {
        console.error('Error:', error);
        showBotMessage("Sorry, there was an error processing your request.");
        textField.val('');
    });
});
