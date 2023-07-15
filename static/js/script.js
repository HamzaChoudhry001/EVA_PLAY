const baseUrl = "http://127.0.0.1:1000/"
var url = baseUrl

// Select2
$(document).ready(function() {
    $('.select2').select2();
});

function movieSelect() {
    let selection = document.getElementById('movieSelect');
    let selectedOption = selection.options[selection.selectedIndex];
    let selectedMovie = selectedOption.value;
    let selectedYear = selectedOption.getAttribute('data-year');
    // if (selectedYear === 'N/A') {
    //     selectedYear = null;
    //     url = baseUrl+"movie/"+selectedMovie;
    //     window.location.href = url;
    // }
    url = baseUrl+"movie/"+selectedMovie+"/"+selectedYear;
    window.location.href = url;
}

function genreSelected(selectedGenre) {
    url = baseUrl + "getByGenre";
    $.post(url, { genre: selectedGenre,
    }, function (data, status) {
        console.log(data, status);
        var htmlContent = "";
        for (var i = 0; i < data[0].genre_movies.length; i++) {
            var movieTitle = data[0].genre_movies[i].replace("'", "%27"); // Replace ' with %27
            htmlContent += `<div class="col-6 col-sm-6 col-md-4 col-lg-4 col-xl-2">
                <div class="video-block">
                    <div class="video-thumb position-relative thumb-overlay">
                        <a href="/movie/${movieTitle}/${data[2].years[i]}"><img class="img-fluid" src="${data[1].genre_posters[i]}" alt=""></a>
                    </div>
                    <div class="video-content">
                        <h2 class="video-title"><a href="/movie/${movieTitle}/${data[2].years[i]}">${data[0].genre_movies[i]}</a></h2>
                    </div>
                    <div class="video-info d-flex align-items-center">
                        <span class="video-year">${data[2].years[i]}</span>
                    </div>
                </div>
            </div>`;
        }
        document.getElementById("genre-row").innerHTML = htmlContent;
    });
}

function yearSelected(selectedYear) {
    url = baseUrl + "getByYear";
    $.post(url, {
        year: selectedYear,
    }, function (data, status) {
        console.log(data, status);
        var htmlContent = "";
        for (var i = 0; i < data[0].year_movies.length; i++) {
            var movieTitle = data[0].year_movies[i].replace("'", "%27"); // Replace ' with %27
            htmlContent += `<div class="col-6 col-sm-6 col-md-4 col-lg-4 col-xl-2">
                <div class="video-block">
                    <div class="video-thumb position-relative thumb-overlay">
                        <a href="/movie/${movieTitle}/${data[2].yeard[i]}"><img class="img-fluid" src="${data[1].year_posters[i]}" alt=""></a>
                    </div>
                    <div class="video-content">
                        <h2 class="video-title"><a href="/movie/${movieTitle}/${data[2].yeard[i]}">${data[0].year_movies[i]}</a></h2>
                    </div>
                    <div class="video-info d-flex align-items-center">
                        <span class="video-year">${data[2].yeard[i]}</span>
                    </div>
                </div>
            </div>`;
        }
        document.getElementById("year-row").innerHTML = htmlContent;
    });
}

const button = document.querySelector(".watch-movie");
const trailer = document.querySelector(".trailer");
const closeButton = document.querySelector(".close");
button.addEventListener('click', () => {
    trailer.style.visibility = "visible";
    trailer.style.opacity = 1;
});

closeButton.addEventListener('click', () => {
    trailer.style.visibility = "hidden";
    trailer.style.opacity = 0;
    const iframe = trailer.querySelector('iframe');
    iframe.src = iframe.src; // stop the video by resetting the source
});  
  
// loader
// $(window).on('load', function() {
//     // Remove the loader when the page is fully loaded
//     $('.loader').fadeOut('slow');
// });

// $(window).on('beforeunload', function() {
//     // Show the loader when the page is being unloaded
//     $('.loader').show();
// });