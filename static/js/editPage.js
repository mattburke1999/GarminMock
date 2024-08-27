let activity1;
let activity2;
function swapActivities() {
    const activity1Element = document.getElementById('merge-activity1');
    const activity2Element = document.getElementById('merge-activity2');
    let activity1HTML = activity1Element.innerHTML.replace('Activity 1', 'Activity 2');
    let activity2HTML = activity2Element.innerHTML.replace('Activity 2', 'Activity 1');
    activity1Element.innerHTML = activity2HTML;
    activity2Element.innerHTML = activity1HTML;
    let temp = activity1;
    activity1 = activity2;
    activity2 = temp;
    localStorage.setItem('activity1', JSON.stringify(activity1));
    localStorage.setItem('activity2', JSON.stringify(activity2));
}
function closeMergeConfirmation() {
    let mergeConfirmationModal = document.getElementById('mergeConfirmation');
    let mergeConfirmation = mergeConfirmationModal.getElementsByClassName('merge-confirmation')[0];
    mergeConfirmation.innerHTML = '';
    mergeConfirmationModal.style.display = 'none';
    localStorage.removeItem('mergeModalDisplayed');
    document.body.classList.remove('hidden');
}

function clearTBody(activtyElement){
    let tbody = activtyElement.getElementsByTagName('tbody')[0];
    tbody.innerHTML = '';
}

function closeMergeActivities() {
    let activty1 = document.getElementById('merge-activity1')
    let activty2 = document.getElementById('merge-activity2')
    clearTBody(activty1);
    clearTBody(activty2);
    let mergeActivitiesModal = document.getElementById('mergeActivities');
    mergeActivitiesModal.style.display = 'none';
    localStorage.removeItem('mergeModalDisplayed');
    document.body.classList.remove('hidden');
    clearSelectedRows();
}
function insert_row_data_into_table(table, row_data) {
    let tbody = table.getElementsByTagName('tbody')[0];
    tbody.innerHTML = '';
    let row = tbody.insertRow();
    let activity_id = row.insertCell(0);
    let title = row.insertCell(1);
    let description = row.insertCell(2);
    let date = row.insertCell(3);
    let sport = row.insertCell(4);
    let time = row.insertCell(5);
    let distance = row.insertCell(6);
    activity_id.style.border = 'none';
    activity_id.innerHTML = `<input type='hidden' value='${row_data.activity_id}'/>`;
    title.innerHTML = row_data.activity_title;
    description.innerHTML = row_data.description;
    date.innerHTML = row_data.start_time;
    sport.innerHTML = row_data.display_sport;
    time.innerHTML = row_data.total_time;
    distance.innerHTML = row_data.total_distance;
}

function open_merge_modal() {
    const activity1Table = document.getElementById('merge-activity1').getElementsByTagName('table')[0];
    const activity2Table = document.getElementById('merge-activity2').getElementsByTagName('table')[0];
    insert_row_data_into_table(activity1Table, activity1);
    insert_row_data_into_table(activity2Table, activity2);
    document.getElementById('mergeActivities').style.display = 'flex';
    document.getElementById('mergeConfirmation').style.display = 'none';
    localStorage.setItem('mergeModalDisplayed', 'true');
    localStorage.setItem('activity1', JSON.stringify(activity1));
    localStorage.setItem('activity2', JSON.stringify(activity2));
    document.body.classList.add('hidden');
}

function show_search_inputs(input_type, div_id, button) {
    var inputs = document.getElementById(div_id).getElementsByTagName('input');
    if (input_type == 'date') {
        inputs[0].style.display = 'block';
        inputs[0].required = true;
        inputs[1].style.display = 'none';
        inputs[1].required = false;
    } else {
        inputs[0].style.display = 'none';
        inputs[0].required = false;
        inputs[1].style.display = 'block';
        inputs[1].required = true;
    }
    var buttons = document.getElementById(div_id).getElementsByClassName('search-options')[0].getElementsByTagName('button');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove('active');
    }
    if (!button.classList.contains('active')){
        button.classList.add('active');
    }
}

function toggleEditOptions() {
    // if 1 row is selected, show edit and delete options
    // if 2 rows are selected, show merge option and delete option
    // if 3 or more rows are selected, show only delete option
    let selected_rows = document.querySelectorAll('input[name="activity_id"]:checked');
    let num_selected = selected_rows.length;
    let edit_btn = document.getElementById('edit-option-edit');
    let merge_btn = document.getElementById('edit-option-merge');
    let delete_btn = document.getElementById('edit-option-delete');
    if(num_selected===0) {
        edit_btn.style.opacity = 0.5;
        edit_btn.style.pointerEvents = 'none';
        edit_btn.disabled = true;
        edit_btn.classList.remove('edit-option-button');
        merge_btn.style.opacity = 0.5;
        merge_btn.style.pointerEvents = 'none';
        merge_btn.disabled = true;
        merge_btn.classList.remove('edit-option-button');
        delete_btn.style.opacity = 0.5;
        delete_btn.style.pointerEvents = 'none';
        delete_btn.disabled = true;
        delete_btn.classList.remove('edit-option-button');
    } else if(num_selected===1) {
        edit_btn.style.opacity = 1;
        edit_btn.style.pointerEvents = 'auto';
        edit_btn.disabled = false;
        if(!edit_btn.classList.contains('edit-option-button')) {
            edit_btn.classList.add('edit-option-button');
        }
        merge_btn.style.opacity = 0.5;
        merge_btn.style.pointerEvents = 'none';
        merge_btn.disabled = true;
        merge_btn.classList.remove('edit-option-button');
        delete_btn.style.opacity = 1;
        delete_btn.style.pointerEvents = 'auto';
        delete_btn.disabled = false;
        if(!delete_btn.classList.contains('edit-option-button')) {
            delete_btn.classList.add('edit-option-button');
        }
    } else if(num_selected===2) {
        edit_btn.style.opacity = 0.5;
        edit_btn.style.pointerEvents = 'none';
        edit_btn.disabled = true;
        edit_btn.classList.remove('edit-option-button');
        merge_btn.style.opacity = 1;
        merge_btn.style.pointerEvents = 'auto';
        merge_btn.disabled = false;
        if(!merge_btn.classList.contains('edit-option-button')) {
            merge_btn.classList.add('edit-option-button');
        }
        delete_btn.style.opacity = 1;
        delete_btn.style.pointerEvents = 'auto';
        delete_btn.disabled = false;
        if(!delete_btn.classList.contains('edit-option-button')) {
            delete_btn.classList.add('edit-option-button');
        }
    } else {
        edit_btn.style.opacity = 0.5;
        edit_btn.style.pointerEvents = 'none';
        edit_btn.disabled = true;
        merge_btn.style.opacity = 0.5;
        merge_btn.style.pointerEvents = 'none';
        merge_btn.disabled = true;
        delete_btn.style.opacity = 1;
        delete_btn.style.pointerEvents = 'auto';
        delete_btn.disabled = false;
        if(!delete_btn.classList.contains('edit-option-button')) {
            delete_btn.classList.add('edit-option-button');
        }
    }
}

function select_row_checkbox(event, row, checkbox) {
    event.stopPropagation();
    if (row !== undefined) {
        checkbox = row.getElementsByClassName('checkbox')[0].getElementsByTagName('input')[0];
    }
    checkbox.checked = !checkbox.checked;
    toggleEditOptions();
}
function select_row_checkbox2(checkbox) {
    checkbox.checked = !checkbox.checked;
    toggleEditOptions();
}

function display_search_results(activity_list) {
    let searchResults = document.getElementById('search-results');
    let table = searchResults.getElementsByTagName('table')[0];
    let tbody = table.getElementsByTagName('tbody')[0];
    tbody.innerHTML = '';
    for (let i = 0; i < activity_list.length; i++) {
        let activity = activity_list[i];
        if (activity['description'].length > 70) {
            activity['description'] = activity['description'].substring(0, 70) + '...';
        }
        let row = tbody.insertRow(i);
        // set the entire row onclick to select the checkbox
        row.onclick = function() {select_row_checkbox(event, this, undefined);};
        row.onmouseover = function() {this.style.backgroundColor = 'lightgray'; this.style.cursor = 'pointer'; this.getElementsByClassName('checkbox')[0].style.backgroundColor = 'white';};
        row.onmouseout = function() {this.style.backgroundColor = 'white';};
        let checkbox = row.insertCell(0);
        checkbox.onclick = function() {select_row_checkbox2(this);};
        let title = row.insertCell(1);
        let description = row.insertCell(2);
        let date = row.insertCell(3);
        let sport = row.insertCell(4);
        let time = row.insertCell(5);
        let distance = row.insertCell(6);
        checkbox.innerHTML = `<input type="checkbox" onclick='select_row_checkbox(event, undefined, this.parentElement)' name="activity_id" value="${activity['activity_id']}">`;
        checkbox.classList.add('checkbox');
        title.innerHTML = activity['activity_title'];
        title.classList.add('search-result-activity-title');
        description.innerHTML = activity['description'];
        description.classList.add('search-result-description');
        date.innerHTML = activity['start_time'];
        date.classList.add('search-result-date');
        sport.innerHTML = activity['display_sport'];
        sport.classList.add('search-result-sport');
        time.innerHTML = activity['total_time'];
        time.classList.add('search-result-time');
        distance.innerHTML = `${activity['total_distance']} ${activity['display_sport']==='Rowing' ? 'm.' : 'mi.'}`;
        distance.classList.add('search-result-distance');
    }
    searchResults.style.display = 'block';            
}
function clearSelectedRows() {
    let selected_rows = document.querySelectorAll('input[name="activity_id"]:checked');
    selected_rows.forEach(row => {
        row.checked = false;
    });
    toggleEditOptions();
}
function search_activities(form, event) {
    event.preventDefault();
    clearSelectedRows();
    let inputs = form.getElementsByTagName('input');
    let $input = inputs[0].style.display !== 'none' ? inputs[0] : inputs[1];
    let input_type = inputs[0].style.display !== 'none' ? 'date' : 'title';
    $.ajax({
        url: '/search_activities_for_edit',
        type: 'GET',
        data: {
            input: $input.value,
            input_type: input_type
        },
        success: function(response) {
            activity_list = response['success'];
            display_search_results(activity_list);
        },
        error: function(response) {
            console.log('error');
            alert('Error searching for activities');
            
        }
    });
}

function getSelectedRowData_merge() {
    let selected_rows = document.querySelectorAll('input[name="activity_id"]:checked');
    let activity_data = [];
    selected_rows.forEach(row => {
        let tr = row.parentElement.parentElement;
        let cells = tr.getElementsByTagName('td');
        let data = {
            'activity_id': row.value,
            'activity_title': cells[1].innerHTML,
            'description': cells[2].innerHTML,
            'start_time': cells[3].innerHTML,
            'display_sport': cells[4].innerHTML,
            'total_time': cells[5].innerHTML,
            'total_distance': cells[6].innerHTML,
            'date_parsed': new Date(cells[3].innerHTML),
        };
        activity_data.push(data);
    });
    // sort by date asc
    activity_data.sort((a, b) => a.date_parsed - b.date_parsed);
    return activity_data;
}
function displayMergeConfirmation(confirm_data) {
    let modal = document.getElementById('mergeConfirmation')
    let mergeConfirmation = modal.getElementsByClassName('merge-confirmation')[0];
    let h2 = mergeConfirmation.getElementsByTagName('h2')[0];
    h2.innerHTML = '';
    if(confirm_data['date_diff']){
        h2.innerHTML = `It appears these activities were tracked ${confirm_data['date_diff']} days apart.`;
    } else { //sport diff
        let sport1 = confirm_data['sport_diff'][0];
        let sport2 = confirm_data['sport_diff'][1];
        h2.innerHTML = `It appears these activities were tracked as different sports: ${sport1} and ${sport2}.`;
    }
    console.log('display')
    modal.style.display = 'flex';
    document.body.classList.add('no-scroll'); // prevents scrolling
}

function merge_check() {
    let activity_data = getSelectedRowData_merge();

    

    activity1 = activity_data[0];
    activity2 = activity_data[1];
    $.ajax({
        url: '/merge_check',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            activity1: activity1,
            activity2: activity2
        }),
        success: function(response) {
            
            if (response.data === '') {
                open_merge_modal();
            } else {
                displayMergeConfirmation(response.data);
            }
        },
        error: function(response) {
            console.log(response.error);
            alert('Error merging activities');
        }
    });
}

function navigate_to_activity() {
    let merged_activity_id = document.getElementById('merged_activity_id').value;
    window.location.href = `/activity/${merged_activity_id}`;
}

function navigate_to_home() {
    window.location.href = '/';
}

function full_reload_page() {
    localStorage.clear();
    window.location.reload();
}

function display_merge_success(merged_activity_id) {
    let modal = document.getElementById('mergeSuccess');
    let input = document.getElementById('merged_activity_id');
    input.value = merged_activity_id;
    modal.style.display = 'flex';
    document.body.classList.add('no-scroll');
}

function merge_activities() {
    $.ajax({
        url: '/merge_activities',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            activity1: activity1.activity_id,
            activity2: activity2.activity_id
        }),
        success: function(response) {
            closeMergeActivities();
            display_merge_success(response.success);
        },
        error: function(response) {
            console.log(response.error);
            closeMergeActivities();
            alert('Error merging activities');
        }
    });
}