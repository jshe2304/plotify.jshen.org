var links = [
    'https://www.coolmathgames.com/',  
    'https://www.youtube.com/watch?v=6gtSe9NXkUg', 
    'https://www.youtube.com/watch?v=dcfV6yUUMhs', 
    'https://ninjakiwi.com/Games/Tower-Defense/Bloons-Tower-Defense-5.html', 
    'https://open.spotify.com/user/fro8ozz',
    'https://open.spotify.com/album/1yfJqxKKXG320vhqLfUEeC',
    'https://www.shitpostbot.com/resize/585/400?img=%2Fimg%2Fsourceimages%2Fthom-yorke-screaming-57c4d13961f43.png'
]

function random_boxes () {
    for (let i = 1; i <= 64; i++) {

        let box = document.createElement('div');

        box.classList.add('box');

        box.style.top = Math.random() * 100 + '%';
        box.style.left = Math.random() * 100 + '%';
        box.style.backgroundColor = 'rgb(' + Math.random() * 255 + ", " + Math.random() * 255 + ", " + Math.random() * 255 + ")";
        box.style.minWidth = Math.random() * 8 + 'em';
        box.style.minHeight = Math.random() * 8 + 'em';

        box.style.backgroundPosition = Math.random() * 100 + '% ' + Math.random() * 100 + "%";

        box.onclick = function () {
            location.href = links[Math.floor(Math.random() * links.length)];
        };

        //box.setAttribute('target', '_blank');

        document.body.appendChild(box);
    }
}

random_boxes()