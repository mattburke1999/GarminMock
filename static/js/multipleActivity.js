let sportFilter = localStorage.getItem('sportFilter');

// on page load, filter posts by sport if sportFilter is set
window.onload = function() {
    console.log(performance.getEntriesByType("navigation")[0].type);
    if (sportFilter) {
        console.log(sportFilter);
        filterPosts(sportFilter, pageload = true);
    }
}

function toggleCollapse(className, button, buttonText) {
    var container = button.parentElement;
    var elements = container.querySelectorAll('.' + className);
    for (var i = 0; i < elements.length; i++) {
        if (elements[i].style.display === "none") {
            if (buttonText === ' Stats') {
                console.log(buttonText)
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
        
$(window).scroll(function(loadMoreEnabled) {
    if (loadMoreEnabled && ($(window).scrollTop() + $(window).height() >= $(document).height() - 100)) {
        loadMoreItems();
    }
});

function setHighlightButton(sport) {
    let filterContainer = document.getElementById('filter-button-container');
    let buttons = Array.from(filterContainer.getElementsByTagName('button'));
    // remove s from class name of button if it exists
    console.log(buttons);
    buttons.forEach(b => {
        b.className = b.className.replace(' s', '');
    });
    if(sport) {
        let button = document.getElementById(`${sport}_filter`);
        button.className += ' s';
    }
    return;
    
}

function filterPosts(sport, pageload=false) {
    if (sport === sportFilter && !pageload) {
        sportFilter = undefined;
        localStorage.removeItem('sportFilter');
    }
    else {
        sportFilter = sport;
        localStorage.setItem('sportFilter', sport);
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
            console.log(data);
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
