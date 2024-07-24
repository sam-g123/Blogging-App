document.addEventListener("DOMContentLoaded", function() {
    var memberSince = moment.utc("{{ member_since_iso }}", moment.ISO_8601).format('L');
    var lastSeen = moment.utc("{{ last_seen_iso }}", moment.ISO_8601).local().fromNow();

    document.getElementById('member-since').textContent = memberSince;
    document.getElementById('last-seen').textContent = lastSeen;
    
    const postDates = document.querySelectorAll('.post-date');
    postDates.forEach(function(postDate) {
        const timestamp = postDate.getAttribute('data-timestamp');
        const formattedDate = moment.utc(timestamp, moment.ISO_8601).local().fromNow();
        postDate.textContent = formattedDate;
    });
});
