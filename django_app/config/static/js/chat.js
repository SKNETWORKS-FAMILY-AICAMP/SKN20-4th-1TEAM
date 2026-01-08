/**
 * 청년이음 챗봇 - 메인 JavaScript
 * Django 프론트엔드용
 */

// ==========================================
// 전역 설정
// ==========================================
// API 엔드포인트 설정 (Django 백엔드 URL)
const API_BASE_URL = '';  // 같은 origin이면 빈 문자열

// 이미지 경로 (Django에서 전달받은 경로 사용)
// main.html에서 window.AVATAR_IMG_PATH로 설정됨
const AVATAR_IMG_PATH = window.AVATAR_IMG_PATH || '/static/assets/images/avatar.png';


// ==========================================
// Placeholder(냥이) 제어 함수
// ==========================================
function showChatPlaceholder() {
    const placeholder = document.getElementById('chat-placeholder');
    const container = document.getElementById('chat-container');

    if (placeholder) placeholder.classList.remove('hidden');
    if (container) container.innerHTML = ''; // 채팅 초기화
}

function hideChatPlaceholder() {
    const placeholder = document.getElementById('chat-placeholder');
    if (placeholder) placeholder.classList.add('hidden');
}

// ==========================================
// 메시지 전송 함수
// ==========================================
async function sendMessage() {
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const message = input.value.trim();

    if (!message) return;

    // 메시지 전송 시 냥이 숨김 (가장 먼저 실행)
    hideChatPlaceholder();

    // 버튼 비활성화 (중복 전송 방지)
    sendBtn.disabled = true;
    sendBtn.classList.add('sending'); // 아이콘 변경 (비행기 -> 네모)

    // 레퍼런스: sendMessage 함수 시작 부분
    // 사용자 메시지 표시
    addMessage(message, 'user');
    input.value = '';

    // 로딩 표시
    const loadingId = addLoadingMessage();

    try {
        // API 호출 (Django 백엔드)
        const formData = new FormData();
        formData.append('question', message);

        const response = await fetch(`${API_BASE_URL}/chat/ask/`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('서버 응답 오류');
        }

        const data = await response.json();

        // 로딩 메시지 제거 후 봇 응답 표시
        removeLoadingMessage(loadingId);
        addMessage(data.answer, 'bot');

    } catch (error) {
        console.error('Error:', error);
        removeLoadingMessage(loadingId);
        addMessage('죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.', 'bot');
    } finally {
        // 버튼 다시 활성화
        sendBtn.disabled = false;
        sendBtn.classList.remove('sending'); // 아이콘 복구
        input.focus();
    }
}

// ==========================================
// 메시지 추가 함수
// ==========================================
function addMessage(text, sender) {
    const container = document.getElementById('chat-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    if (sender === 'bot') {
        // 봇 메시지는 마크다운으로 렌더링 (줄바꿈을 <br>로 변환)
        marked.setOptions({ breaks: true });
        const renderedHtml = marked.parse(text);
        messageDiv.innerHTML = `
            <div class="avatar">
                <img src="${AVATAR_IMG_PATH}" alt="봇 아바타" onerror="this.style.display='none'; this.parentElement.classList.add('avatar-placeholder');">
            </div>
            <div class="message-bubble markdown-content">
                ${renderedHtml}
            </div>
        `;
    } else {
        // 사용자 메시지는 일반 텍스트
        messageDiv.innerHTML = `
            <div class="message-bubble">
                <p>${escapeHtml(text)}</p>
            </div>
        `;
    }

    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

// ==========================================
// 로딩 메시지
// ==========================================
function addLoadingMessage() {
    const container = document.getElementById('chat-container');
    const loadingId = 'loading-' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.id = loadingId;
    loadingDiv.className = 'message bot-message loading-message';
    loadingDiv.innerHTML = `
        <div class="avatar">
            <img src="${AVATAR_IMG_PATH}" alt="봇 아바타" onerror="this.style.display='none'; this.parentElement.classList.add('avatar-placeholder');">
        </div>
        <div class="message-bubble">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    container.appendChild(loadingDiv);
    container.scrollTop = container.scrollHeight;
    return loadingId;
}

function removeLoadingMessage(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// ==========================================
// 유틸리티 함수
// ==========================================
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==========================================
// 헤더 버튼 기능
// ==========================================
function handleNewChat() {
    console.log('새 채팅 버튼 클릭');
    if (confirm('새로운 채팅을 시작하시겠습니까?')) {
        showChatPlaceholder(); // 냥이 표시 및 채팅 초기화
    }
}

// ==========================================
// 폰트 크기 조절 기능
// ==========================================
const fontSizes = ['level1', 'level2', 'level3'];
let currentFontSizeIndex = 0;

function handleFontSize() {
    currentFontSizeIndex = (currentFontSizeIndex + 1) % fontSizes.length;
    const size = fontSizes[currentFontSizeIndex];

    const root = document.documentElement;
    switch (size) {
        case 'level1':
            // 기본 (0.9배) - 사용자가 요청한 비율 복구
            root.style.setProperty('--font-size-base', 'clamp(0.8rem, 0.75rem + 0.45vw, 1rem)');
            root.style.setProperty('--font-size-sm', 'clamp(0.675rem, 0.65rem + 0.35vw, 0.9rem)');
            root.style.setProperty('--font-size-lg', 'clamp(0.9rem, 0.85rem + 0.55vw, 1.15rem)');
            break;
        case 'level2':
            // 확대 (1.0배) - CSS 기본값과 동일
            root.style.setProperty('--font-size-base', 'clamp(0.875rem, 0.8rem + 0.5vw, 1.125rem)');
            root.style.setProperty('--font-size-sm', 'clamp(0.75rem, 0.7rem + 0.4vw, 1rem)');
            root.style.setProperty('--font-size-lg', 'clamp(1rem, 0.9rem + 0.6vw, 1.25rem)');
            break;
        case 'level3':
            // 최대 확대 (약 1.15배)
            root.style.setProperty('--font-size-base', 'clamp(1rem, 0.9rem + 0.6vw, 1.25rem)');
            root.style.setProperty('--font-size-sm', 'clamp(0.875rem, 0.8rem + 0.5vw, 1.125rem)');
            root.style.setProperty('--font-size-lg', 'clamp(1.125rem, 1rem + 0.7vw, 1.375rem)');
            break;
    }

    const btn = document.getElementById('btn-font-size');
    const labels = { level1: 'Aa', level2: 'Aa²', level3: 'Aa³' };
    btn.querySelector('.icon-text').textContent = labels[size];

    console.log(`폰트 크기 변경: ${size}`);
}

// ==========================================
// 대화 저장 기능
// ==========================================
function handleSave() {
    const container = document.getElementById('chat-container');
    const messages = container.querySelectorAll('.message');

    if (messages.length === 0) {
        alert('저장할 대화 내용이 없습니다.');
        return;
    }

    let chatText = '=== 청년이음 대화 기록 ===\n';
    chatText += `저장 시간: ${new Date().toLocaleString('ko-KR')}\n`;
    chatText += '========================\n\n';

    messages.forEach((msg) => {
        const isBot = msg.classList.contains('bot-message');
        const sender = isBot ? '🤖 선배봇' : '👤 나';
        const bubble = msg.querySelector('.message-bubble');
        if (bubble) {
            const text = bubble.innerText.trim();
            chatText += `${sender}:\n${text}\n\n`;
        }
    });

    const blob = new Blob([chatText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `청년이음_대화기록_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('대화 저장 완료');
}

// ==========================================
// 도움말 모달 기능
// ==========================================
const helpContent = `
    <h1>반가워! 청년들의 든든한 정책 선배, 청년이음 선배봇이야! 🌟🤖</h1>
    <p>안녕, 후배님! 👋 여기까지 찾아오느라 고생 많았어.<br>
    나는 <strong>주거, 일자리, 복지, 금융</strong> 등 복잡하고 어려운 청년 정책들을<br>
    너에게 딱 맞춰서 알기 쉽게 설명해 주는 <strong>AI 정책 멘토</strong>야.</p>
    <p>어떤 정보가 필요한지 말만 해! 방대한 정책 데이터 속에서 네 상황에 딱 맞는 꿀팁들만 쏙쏙 골라줄게. 😺</p>
    <hr>
    <h2>💡 나한테 이렇게 물어봐!</h2>
    <p>막연하게 질문해도 괜찮지만, <strong>사는 곳</strong>이나 <strong>관심 분야</strong>를 함께 말해주면 더 정확하게 알려줄 수 있어!</p>
    
    <h3>🏠 주거 & 자취</h3>
    <ul>
        <li>"서울에서 자취 중인데 월세 지원 받을 수 있어?"</li>
        <li>"대구 행복주택 입주 자격이 어떻게 돼?"</li>
        <li>"전세 보증금 이자 지원 정책 좀 찾아줄래?"</li>
    </ul>
    
    <h3>💼 취업 & 일자리</h3>
    <ul>
        <li>"경기도 취업 면접 수당 신청하고 싶어."</li>
        <li>"미취업 청년을 위한 지원금 있을까?"</li>
        <li>"내일배움카드 발급 방법 좀 알려줘."</li>
    </ul>
    
    <h3>🍀 복지 & 금융</h3>
    <ul>
        <li>"청년도약계좌 가입 조건이 뭐야?"</li>
        <li>"마음 건강 상담 받고 싶은데 지원 정책 있어?"</li>
        <li>"학자금 대출 이자 지원 신청 기간 언제야?"</li>
    </ul>
    <hr>
    <h2>📝 꿀팁 대방출!</h2>
    <ol>
        <li><strong>지역을 콕 집어줘!</strong> 🗺️<br>"그냥 지원금 줘" 대신 <strong>"인천 지원금 줘"</strong>라고 하면 더 정확해!</li>
        <li><strong>구체적으로 물어봐!</strong> 🔍<br>너의 나이, 소득, 거주지 상황을 살짝 귀띔해주면 맞춤형 상담이 가능해.</li>
        <li><strong>생각의 과정도 슬쩍 봐봐!</strong> 🧠<br>답변 아래에 있는 <strong>[🔍 선배봇의 생각 과정 보기]</strong>를 누르면, 내가 어떻게 자료를 찾았는지 보여줄게.</li>
    </ol>
    <p>자, 이제 시작해볼까? 궁금한 거 있으면 편하게 물어봐! 힘껏 도와줄게! 💪😊</p>
`;

function handleHelp() {
    const modal = document.getElementById('help-modal');
    const content = document.getElementById('help-content');
    content.innerHTML = helpContent;
    modal.classList.add('active');
    console.log('도움말 모달 열림');
}

function closeHelpModal(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById('help-modal');
    modal.classList.remove('active');
}

// ==========================================
// 맞춤 설정 모달 기능
// ==========================================
function handleSettings() {
    const modal = document.getElementById('settings-modal');
    modal.classList.add('active');
    console.log('설정 모달 열림');
}

function closeSettingsModal(event) {
    if (event && event.target !== event.currentTarget) return;
    const modal = document.getElementById('settings-modal');
    modal.classList.remove('active');
}

// ==========================================
// 이벤트 리스너 초기화
// ==========================================
document.addEventListener('DOMContentLoaded', function () {
    const messageInput = document.getElementById('message-input');

    if (messageInput) {
        // 입력창 자동 높이 조절
        messageInput.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 72) + 'px'; // 최대 3줄(72px)
        });

        // Enter 키로 메시지 전송 (Shift+Enter는 줄바꿈)
        messageInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // ESC 키로 모달 닫기
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeHelpModal();
            closeSettingsModal();
            // 사이드바도 닫기 (모바일)
            const sidebar = document.getElementById('sidebar');
            if (sidebar && sidebar.classList.contains('open')) {
                toggleSidebar();
            }
        }
    });
});

// ==========================================
// 사이드바 토글 함수
// ==========================================
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const isMobile = window.innerWidth <= 768;

    if (sidebar) {
        if (isMobile) {
            // 모바일: open 클래스로 드로어 열기
            sidebar.classList.toggle('open');
            if (overlay) {
                overlay.classList.toggle('active');
            }
            // body 스크롤 제어
            if (sidebar.classList.contains('open')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        } else {
            // 데스크탑: collapsed 클래스로 사이드바 접기
            sidebar.classList.toggle('collapsed');
            document.body.classList.toggle('sidebar-collapsed');
        }
    }
}

// ==========================================
// 추천 질문 입력 함수
// ==========================================
function setInputValue(text) {
    const input = document.getElementById('message-input');
    if (input) {
        input.value = text;
        input.focus();
    }
}
