document.addEventListener('DOMContentLoaded', function () {
    // Example: Add client-side validation for the event form
    const eventForm = document.querySelector('form');
    const dateInput = document.getElementById('date');
    const eventInput = document.getElementById('event');

    eventForm.addEventListener('submit', function (e) {
        // Prevent form submission if inputs are empty
        if (!dateInput.value || !eventInput.value) {
            alert('Both date and event description are required!');
            e.preventDefault();
        }
    });

    // Example: Fetch and display today's events without reloading the page
    const fetchTodayEventsButton = document.getElementById('fetch-today-events');
    if (fetchTodayEventsButton) {
        fetchTodayEventsButton.addEventListener('click', function () {
            fetch('/api/today')
                .then(response => response.json())
                .then(data => {
                    const eventsList = document.getElementById('today-events');
                    eventsList.innerHTML = '';  // Clear the list
                    if (data.message) {
                        eventsList.innerHTML = `<li>${data.message}</li>`;
                    } else {
                        data.forEach(event => {
                            const listItem = document.createElement('li');
                            listItem.textContent = event;
                            eventsList.appendChild(listItem);
                        });
                    }
                })
                .catch(error => console.error('Error fetching today\'s events:', error));
        });
    }
});
