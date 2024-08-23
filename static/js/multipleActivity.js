let sportFilter = undefined;

function toggleCollapse(className, button, buttonText) {
    var container = button.parentElement;
    var elements = container.querySelectorAll('.' + className);
    for (var i = 0; i < elements.length; i++) {
        if (elements[i].style.display === "none") {
            if (buttonText === ' Stats') {
                elements[i].style.display = "grid";
            } else {
                elements[i].style.display = "block";
            }
            button.innerHTML = "Hide";
            button.style.marginBottom = "10px"
        } else {
            elements[i].style.display = "none";
            button.innerHTML = "View " + buttonText;
            button.style.marginBottom = "0px"
        }
    }
}

function navigateToActivity(index) {
    let activity = activities[index];
    let lap_html = lap_htmls[index];
    let folium_map = maps[index];

    document.getElementById('activity-input').value = JSON.stringify(activity);
    document.getElementById('lap-input').value = lap_html;
    document.getElementById('map-input').value = folium_map;

    document.getElementById('activity-form').submit();
}

let offset = 15;
        
$(window).scroll(function() {
    if (loadMoreEnabled) {
        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 100) {
                loadMoreItems();
                return;
        }
    }
});

function setHighlightButton(sport) {
    let filterContainer = document.getElementById('filter-button-container');
    let buttons = Array.from(filterContainer.getElementsByTagName('button'));
    // remove s from class name of button if it exists
    buttons.forEach(b => {
        b.className = b.className.replace(' s', '');
    });
    if(sport) {
        let button = document.getElementById(`${sport}_filter`);
        button.className += ' s';
    }
    return;
    
}

function filterPosts(sport) {
    if (sport === sportFilter) {
        sportFilter = undefined;
    }
    else {
        sportFilter = sport;
    }
    $('#posts-container').html('');
    $('#loading').show();
    setHighlightButton(sport);
    $.ajax({
        url: '/filter_posts',
        type: 'GET',
        data: {
            sport: sportFilter
        },
        success: function(data) {
            $('#loading').hide();
            $('#posts-container').html(data[1]);
            offset = 15;
        },
        error: function() {
            $('#loading').hide();
            console.error('Error filtering posts');
        }
    });
}

function loadMoreItems() {
    if ($('#loading').is(':visible')) return;

    $('#loading').show();

    $.ajax({
        url: '/load_more',
        type: 'GET',
        data: {
            offset: offset,
            sport: sportFilter
        },
        success: function(data) {
            if (data.length > 0) {
                data[1].forEach(itemHtml => {
                    $('#posts-container').append(itemHtml);
                });
                offset += 10;
            }
            $('#loading').hide();
        },
        error: function() {
            console.error('Error loading more items');
            $('#loading').hide();
        }
    });
}

function closeUnMergeConfirmation() {
    let confirmModal = document.getElementById('unmergeConfirmation');
    confirmModal.style.display = 'none';
    document.body.classList.remove('no-scroll');
}

function unmerge_activity_final() {
    let id_input = document.getElementById('merge-id');
    let id = id_input.value;
    console.log(`MERGE ID: ${id}`);
    $.ajax({
        url: '/unmerge_activity',
        contentType: 'application/json',
        type: 'POST',
        data: JSON.stringify({merge_id: id}),
        success: function() {
            window.location.reload();
        },
        error: function(error) {
            console.error('Error unmerging activity');
            console.log(error.responseText);
            closeUnMergeConfirmation();
            alert('Error unmerging activity');
        }
    });

}

function displayConfirmUnmerge(id, issue_message) {
    // this will display the confirm unmerge modal
    let confirmModal = document.getElementById('unmergeConfirmation');
    let h2 = confirmModal.getElementsByTagName('h2')[0];
    let id_input = document.getElementById('merge-id');
    id_input.value = id;
    h2.innerHTML = issue_message ? issue_message : '';
    confirmModal.style.display = 'flex';
    document.body.classList.add('no-scroll');
}

function unmergeActivity(index) {
    let activity_id = activities[index].activity_id;
    $.ajax({
        url: '/unmerge_check',
        contentType: 'application/json',
        type: 'POST',
        data: JSON.stringify({activity_id: activity_id}),
        success: function(data) {
            // if the activity has been merged and can be merged with no issues,
            // return will be the DB id of the merged activity from merged_actvities table and '' for no issue
            
            // if the activity has been merged, but unmerging will cause issues (ie, the merged activity has been edited),
            // return will be the DB id of the merged activity from merged_actvities table and issue message

            // proceed to confirm unmerge with issue message if exists
            if (data['data'][0] !== 'cannot unmerge'){
                displayConfirmUnmerge(data['data'][0], data['data'][1]);
            } else {
                // if cannot be unmerged, return will be 'cannot unmerge' with issue message
                // and will display alert that activity cannot be unmerged
                // due to issue message
                alert(`Activity cannot be unmerged due to the following issue: ${data[1]}`);
            }
        },
        error: function(error) {
            console.error('Error unmerging activities');
            console.log(error.responseText);
            alert('Error unmerging activities');
        }
    });
}
