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
