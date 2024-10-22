document.addEventListener('DOMContentLoaded', function() {
    console.log('Custom JavaScript loaded');

    var targetTypeField = document.querySelector('#id_target_type');
    var departmentField = document.querySelector('#id_department');  // Updated selector
    var userField = document.querySelector('#id_user');  // Updated selector

    function toggleFields() {
        var targetType = targetTypeField.value;

        if (targetType === 'ALL') {
            departmentField.style.display = 'none';
            userField.style.display = 'none';
        } else if (targetType === 'DEPT') {
            departmentField.style.display = '';
            userField.style.display = 'none';
        } else if (targetType === 'USER') {
            departmentField.style.display = 'none';
            userField.style.display = '';
        }
    }

    // Initial call to set fields based on the current target type
    toggleFields();

    // Event listener for changes in the target type field
    targetTypeField.addEventListener('change', function() {
        toggleFields();
    });
});
