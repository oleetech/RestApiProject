notification = {
    primary: function (message, from, align) {
        const notyf = new Notyf({
            position: {
                x: align, // left or right
                y: from, // bottom or top
            },
            types: [
                {
                    type: 'info',
                    background: '#262B40',
                    icon: {
                        className: 'fas fa-comment-dots',
                        tagName: 'span',
                        color: '#fff'
                    },
                    dismissible: false,
                    speed: 9000
                }
            ]
        });
        notyf.open({
            type: 'info',
            message: message
        });
    },
    info: function (message, from, align) {
        const notyf = new Notyf({
            position: {
                x: align, // left or right
                y: from, // bottom or top
            },
            types: [
                {
                    type: 'info',
                    background: '#0948B3',
                    icon: {
                        className: 'fas fa-comment-dots',
                        tagName: 'span',
                        color: '#fff'
                    },
                    dismissible: false
                }
            ]
        });
        notyf.open({
            type: 'info',
            message: message
        });
    },
    success: function (message, from, align) {
        const notyf = new Notyf({
            position: {
                x: align, // left or right
                y: from, // bottom or top
            },
            types: [
                {
                    type: 'info',
                    background: '#92f16d',
                    icon: {
                        className: 'fas fa-comment-dots',
                        tagName: 'span',
                        color: '#fff'
                    },
                    dismissible: false
                }
            ]
        });
        notyf.open({
            type: 'info',
            message: message
        });
    },
    warning: function (message, from, align) {
        const notyf = new Notyf({
            position: {
                x: align, // left or right
                y: from, // bottom or top
            },
            types: [
                {
                    type: 'warning',
                    background: '#F5B759',
                    icon: {
                        className: 'fas fa-comment-dots',
                        tagName: 'span',
                        color: '#fff'
                    },
                    dismissible: false
                }
            ],
            delay: 9000
        });
        notyf.open({
            type: 'warning',
            message: message
        });
    },
    danger: function (message, from, align) {
        const notyf = new Notyf({
            position: {
                x: align, // left or right
                y: from, // bottom or top
            },
            types: [
                {
                    type: 'error',
                    background: '#FA5252',
                    icon: {
                        className: 'fas fa-comment-dots',
                        tagName: 'span',
                        color: '#fff'
                    },
                    dismissible: false
                }
            ]
        });
        notyf.open({
            type: 'error',
            message: message
        });
    }
};

const checkboxs = document.querySelectorAll('input[type=checkbox]');
for (var i = 0; i < checkboxs.length; i++) {
    checkboxs[i].classList.add('form-check-input');
}

const texts = document.querySelectorAll('select');
for (var y = 0; y < texts.length; y++) {
    texts[y].classList.add('form-select');
}

const r = document.querySelectorAll('input[type=text], input[type=email], input[type=password], input[type=number], textarea');
for (var z = 0; z < r.length; z++) {
    r[z].classList.add('form-control');
}


document.addEventListener('DOMContentLoaded', function() {
    // Select all file input elements
    const fileInputs = document.querySelectorAll('input[type="file"]');

    fileInputs.forEach(function(input) {
        // Add the custom CSS class
        input.classList.add('form-control');

        // Update the appearance of the input when a file is selected
        input.addEventListener('change', function() {
            if (input.files.length > 0) {
                // You can add additional logic here if needed
            }
        });
    });
});


// Wait for the DOM content to load
document.addEventListener('DOMContentLoaded', function() {
    // Select the <select> element using its name attribute
    const subscriptionSelect = document.querySelector('select[name="subscription"]');

    // Check if the <select> element exists
    if (subscriptionSelect) {
        // Remove the 'related-widget-wrapper' class from its parent element
        const parentWrapper = subscriptionSelect.closest('.related-widget-wrapper');
        if (parentWrapper) {
            parentWrapper.classList.remove('related-widget-wrapper');
        }

        // Add 'form-group mb-2' class to the parent element
        if (parentWrapper) {
            parentWrapper.classList.add('form-group', 'mb-2');
        }
    }
});


