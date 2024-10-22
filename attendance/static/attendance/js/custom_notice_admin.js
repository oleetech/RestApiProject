document.addEventListener('DOMContentLoaded', function() {
    console.log('Custom JavaScript loaded');

    var targetTypeField = document.querySelector('#id_target_type');
    var departmentField = document.querySelector('#id_department');  // Updated selector
    var userField = document.querySelector('#id_user');  // Updated selector

    function toggleFields() {
        var targetType = targetTypeField.value;

        // Get grandparent divs of the fields
        var departmentGrandparentDiv = departmentField.parentElement.parentElement; // Adjust selector if necessary
        var userGrandparentDiv = userField.parentElement.parentElement; // Adjust selector if necessary

        if (targetType === 'ALL') {
            // Hide both grandparent divs
            departmentGrandparentDiv.style.display = 'none'; 
            userGrandparentDiv.style.display = 'none';
        } else if (targetType === 'DEPT') {
            // Show department grandparent div and hide user grandparent div
            departmentGrandparentDiv.style.display = ''; 
            userGrandparentDiv.style.display = 'none';
        } else if (targetType === 'USER') {
            // Hide department grandparent div and show user grandparent div
            departmentGrandparentDiv.style.display = 'none'; 
            userGrandparentDiv.style.display = ''; 
        }
    }

    // Initial call to set fields based on the current target type
    toggleFields();

    // Event listener for changes in the target type field
    targetTypeField.addEventListener('change', function() {
        toggleFields();
    });
});
