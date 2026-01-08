/**
 * main.js - 랜딩 페이지 로직 (방향별 회전 애니메이션)
 */

const IMG_PATH_CHAT = '/static/assets/images/chat.png';
const IMG_PATH_SEARCH = '/static/assets/images/search.png';

/**
 * 페이지 전환 처리
 * @param {string} targetUrl - 이동할 URL
 * @param {string} imagePath - 전환 이미지 경로
 * @param {string} direction - 회전 방향 ('left' 또는 'right')
 */
function handleTransition(targetUrl, imagePath, direction) {
    const card = document.getElementById('main-card');
    const transitionImg = document.getElementById('transition-img');

    if (card && transitionImg) {
        // 1. 뒷면 이미지 설정
        transitionImg.src = imagePath;

        // 2. 방향에 따라 회전 클래스 추가
        if (direction === 'left') {
            card.classList.add('rotate-left');
        } else {
            card.classList.add('rotate-right');
        }

        // 3. 1.5초(1500ms) 대기 후 페이지 이동 (URL이 있을 때만)
        setTimeout(() => {
            if (targetUrl) {
                window.location.href = targetUrl;
            }
            // URL이 없으면 전환 효과만 보여주고 멈춤
        }, 1500);
    } else {
        // Fallback: 요소가 없으면 바로 이동
        window.location.href = targetUrl;
    }
}

function goToChat() {
    // 버튼1: 왼쪽으로 회전, chat.png 표시 후 chat 페이지로 이동
    handleTransition('/chat/chat/', IMG_PATH_CHAT, 'left');
}

function goToSearch() {
    // 버튼2: 오른쪽으로 회전, search.png 표시 후 search 페이지로 이동
    handleTransition('/chat/search/', IMG_PATH_SEARCH, 'right');
}
