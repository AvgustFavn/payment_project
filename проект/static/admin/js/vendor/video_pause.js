// Получаем ссылки на все видео элементы
const videos = document.querySelectorAll('video');

// Добавляем обработчики событий на все видео элементы
videos.forEach(video => {
video.addEventListener('play', () => {
// При запуске плеера, приостанавливаем остальные плееры
videos.forEach(v => {
if (v !== video) {
v.pause();
}
});
});
});