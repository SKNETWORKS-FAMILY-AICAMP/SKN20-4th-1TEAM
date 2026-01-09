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
// 메시지 전송 상태 관리
// ==========================================
let currentAbortController = null;
let isSending = false;

/**
 * 전송/정지 버튼 핸들러
 */
function handleSendButton() {
    if (isSending) {
        stopMessage();
    } else {
        sendMessage();
    }
}

/**
 * 메시지 전송 중지
 */
function stopMessage() {
    if (currentAbortController) {
        currentAbortController.abort();
        console.log('메시지 전송 중지됨');
    }
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

    // 전송 상태 설정
    isSending = true;
    currentAbortController = new AbortController();
    sendBtn.classList.add('sending'); // 아이콘 변경 (비행기 -> 네모)

    // 1. 사용자 메시지 표시 + localStorage 저장
    addMessage(message, 'user');
    saveMessage('user', message);

    // 2. [추가] 내가 보낸 질문이 바로 보이도록 스크롤 내리기
    const container = document.getElementById('chat-container');
    container.scrollTop = container.scrollHeight;
    container.scrollTop += 100;

    input.value = '';

    // 로딩 표시
    const loadingId = addLoadingMessage();

    try {
        // API 호출 (Django 백엔드)
        const formData = new FormData();
        formData.append('question', message);

        const response = await fetch(`${API_BASE_URL}/chat/ask/`, {
            method: 'POST',
            body: formData,
            signal: currentAbortController.signal  // 취소 시그널 연결
        });

        if (!response.ok) {
            throw new Error('서버 응답 오류');
        }

        const data = await response.json();

        // 로딩 메시지 제거 후 봇 응답 표시 + localStorage 저장
        removeLoadingMessage(loadingId);
        addMessage(data.answer, 'bot');
        saveMessage('bot', data.answer);

    } catch (error) {
        removeLoadingMessage(loadingId);

        if (error.name === 'AbortError') {
            // 사용자가 정지 버튼을 누른 경우
            addMessage('응답 생성이 중지되었습니다.', 'bot');
            console.log('요청이 사용자에 의해 취소됨');
        } else {
            console.error('Error:', error);
            addMessage('죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.', 'bot');
        }
    } finally {
        // 상태 초기화
        isSending = false;
        currentAbortController = null;
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
// 현재 대화 상태 관리
// ==========================================
let currentConversationId = null;

// ==========================================
// 헤더 버튼 기능
// ==========================================
function handleNewChat() {
    console.log('새 채팅 버튼 클릭');
    if (confirm('새로운 채팅을 시작하시겠습니까?')) {
        setCurrentChatId(null); // 현재 대화 초기화
        showChatPlaceholder(); // 냥이 표시 및 채팅 초기화
        loadChatHistory(); // 목록 갱신 (활성 상태 업데이트)
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
        // Mac 한글 입력 시 이중 전송 방지를 위해 isComposing 체크
        messageInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
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
        sendMessage(); // 바로 전송
    }
}

// ==========================================
// 채팅 기록 관리 - localStorage 기반
// ==========================================

const STORAGE_KEY_CHAT_LIST = 'youth_chat_list';
const STORAGE_KEY_CURRENT_ID = 'youth_current_chat_id';
const MAX_CHAT_COUNT = 20;

/**
 * localStorage에서 채팅 목록 가져오기
 * @returns {Array} 대화 목록
 */
function getChatList() {
    try {
        const data = localStorage.getItem(STORAGE_KEY_CHAT_LIST);
        return data ? JSON.parse(data) : [];
    } catch (e) {
        console.error('채팅 목록 로드 실패:', e);
        return [];
    }
}

/**
 * localStorage에 채팅 목록 저장
 * @param {Array} list - 저장할 대화 목록
 */
function saveChatList(list) {
    try {
        localStorage.setItem(STORAGE_KEY_CHAT_LIST, JSON.stringify(list));
    } catch (e) {
        console.error('채팅 목록 저장 실패:', e);
        // 용량 부족 시 오래된 대화 삭제 후 재시도
        if (e.name === 'QuotaExceededError') {
            autoCleanOldChats(true);
            try {
                localStorage.setItem(STORAGE_KEY_CHAT_LIST, JSON.stringify(list));
            } catch (e2) {
                console.error('용량 정리 후에도 저장 실패:', e2);
            }
        }
    }
}

/**
 * 현재 활성 대화 ID 가져오기
 */
function getCurrentChatId() {
    return localStorage.getItem(STORAGE_KEY_CURRENT_ID);
}

/**
 * 현재 활성 대화 ID 설정
 */
function setCurrentChatId(id) {
    if (id) {
        localStorage.setItem(STORAGE_KEY_CURRENT_ID, id);
    } else {
        localStorage.removeItem(STORAGE_KEY_CURRENT_ID);
    }
    currentConversationId = id;
}

/**
 * 새 대화 생성
 * @returns {Object} 새로 생성된 대화 객체
 */
function createNewChat() {
    const newChat = {
        id: 'chat_' + Date.now(),
        title: null, // 첫 질문 시 설정됨
        createdAt: new Date().toISOString(),
        messages: []
    };

    const list = getChatList();
    list.unshift(newChat); // 맨 앞에 추가
    saveChatList(list);
    setCurrentChatId(newChat.id);

    return newChat;
}

/**
 * 현재 대화에 메시지 저장
 * @param {string} role - 'user' 또는 'bot'
 * @param {string} content - 메시지 내용
 */
function saveMessage(role, content) {
    let list = getChatList();
    let chatId = getCurrentChatId();

    // 현재 대화가 없으면 새로 생성
    if (!chatId) {
        const newChat = createNewChat();
        chatId = newChat.id;
        list = getChatList();
    }

    const chatIndex = list.findIndex(c => c.id === chatId);
    if (chatIndex === -1) {
        // 목록에 없으면 새로 생성
        const newChat = createNewChat();
        list = getChatList();
        const newIndex = list.findIndex(c => c.id === newChat.id);
        if (newIndex !== -1) {
            list[newIndex].messages.push({ role, content });
            // 첫 사용자 메시지를 제목으로 설정
            if (role === 'user' && !list[newIndex].title) {
                list[newIndex].title = content.length > 30
                    ? content.substring(0, 30) + '...'
                    : content;
            }
            saveChatList(list);
            loadChatHistory(); // 목록 갱신
        }
        return;
    }

    list[chatIndex].messages.push({ role, content });

    // 첫 사용자 메시지를 제목으로 설정
    if (role === 'user' && !list[chatIndex].title) {
        list[chatIndex].title = content.length > 30
            ? content.substring(0, 30) + '...'
            : content;
    }

    saveChatList(list);
    loadChatHistory(); // 목록 갱신
}

/**
 * 채팅 기록 목록 불러오기 및 렌더링
 */
function loadChatHistory() {
    const conversations = getChatList();
    renderChatList(conversations);
}

/**
 * 채팅 목록을 사이드바에 동적 렌더링
 * @param {Array} conversations - 대화 목록
 */
function renderChatList(conversations) {
    const listContainer = document.getElementById('chat-history-list');
    if (!listContainer) return;

    listContainer.innerHTML = '';

    if (conversations.length === 0) {
        listContainer.innerHTML = '<li class="history-empty">대화 기록이 없습니다</li>';
        return;
    }

    const currentId = getCurrentChatId();

    conversations.forEach(conv => {
        const li = document.createElement('li');
        li.className = 'history-item' + (conv.id === currentId ? ' active' : '');
        li.dataset.conversationId = conv.id;

        const title = conv.title && conv.title.length > 20
            ? conv.title.substring(0, 20) + '...'
            : (conv.title || '새 대화');

        li.innerHTML = `
            <span class="history-title" onclick="loadConversation('${conv.id}')">${escapeHtml(title)}</span>
            <button class="chat-menu-btn" onclick="toggleChatMenu(event, '${conv.id}')" aria-label="메뉴">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="5" r="2"></circle>
                    <circle cx="12" cy="12" r="2"></circle>
                    <circle cx="12" cy="19" r="2"></circle>
                </svg>
            </button>
            <div class="chat-dropdown" id="dropdown-${conv.id}">
                <button class="chat-dropdown-item" onclick="renameChat('${conv.id}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                    이름 수정
                </button>
                <button class="chat-dropdown-item delete" onclick="deleteChat('${conv.id}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                    삭제
                </button>
            </div>
        `;

        listContainer.appendChild(li);
    });
}

/**
 * 특정 대화 불러오기
 * @param {string} chatId - 대화 ID
 */
function loadConversation(chatId) {
    const list = getChatList();
    const chat = list.find(c => c.id === chatId);

    if (!chat) {
        console.error('대화를 찾을 수 없습니다:', chatId);
        return;
    }

    setCurrentChatId(chatId);

    // UI 활성 상태 업데이트
    document.querySelectorAll('.history-item').forEach(item => {
        item.classList.toggle('active', item.dataset.conversationId === chatId);
    });

    closeAllDropdowns();

    // 채팅 영역 초기화 및 메시지 표시
    const container = document.getElementById('chat-container');
    container.innerHTML = '';
    hideChatPlaceholder();

    if (chat.messages && chat.messages.length > 0) {
        chat.messages.forEach(msg => {
            addMessage(msg.content, msg.role);
        });
        container.scrollTop = container.scrollHeight;
    }

    console.log('대화 불러오기 완료:', chatId);
}

/**
 * 채팅방 이름 수정
 * @param {string} chatId - 대화 ID
 */
function renameChat(chatId) {
    closeAllDropdowns();

    const list = getChatList();
    const chatIndex = list.findIndex(c => c.id === chatId);

    if (chatIndex === -1) return;

    const currentTitle = list[chatIndex].title || '';
    const newName = prompt('새 이름을 입력하세요:', currentTitle);

    if (!newName || !newName.trim()) return;

    list[chatIndex].title = newName.trim();
    saveChatList(list);
    loadChatHistory();

    console.log('이름 수정 완료:', chatId);
}

/**
 * 채팅방 삭제
 * @param {string} chatId - 대화 ID
 */
function deleteChat(chatId) {
    closeAllDropdowns();

    if (!confirm('이 대화를 삭제하시겠습니까?')) return;

    let list = getChatList();
    list = list.filter(c => c.id !== chatId);
    saveChatList(list);

    // 현재 보던 대화였으면 초기화
    if (getCurrentChatId() === chatId) {
        setCurrentChatId(null);
        showChatPlaceholder();
    }

    loadChatHistory();
    console.log('대화 삭제 완료:', chatId);
}

/**
 * 오래된 대화 자동 삭제
 * @param {boolean} force - 즉시 삭제 여부 (용량 부족 시)
 */
function autoCleanOldChats(force = false) {
    let list = getChatList();

    // 20개 초과 시 오래된 것부터 삭제
    if (list.length > MAX_CHAT_COUNT || force) {
        // createdAt 기준 정렬 (최신 먼저)
        list.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));

        // 상위 20개만 유지
        const toKeep = force ? MAX_CHAT_COUNT - 5 : MAX_CHAT_COUNT;
        list = list.slice(0, toKeep);

        saveChatList(list);
        console.log(`오래된 대화 정리 완료. 현재 ${list.length}개 유지.`);
    }
}

/**
 * 채팅 메뉴 드롭다운 토글
 * @param {Event} event - 클릭 이벤트
 * @param {string} conversationId - 대화 ID
 */
function toggleChatMenu(event, conversationId) {
    event.stopPropagation();

    const dropdown = document.getElementById(`dropdown-${conversationId}`);
    const isOpen = dropdown.classList.contains('open');

    // 다른 드롭다운 모두 닫기
    closeAllDropdowns();

    // 현재 드롭다운 토글
    if (!isOpen) {
        dropdown.classList.add('open');
    }
}

/**
 * 모든 드롭다운 닫기
 */
function closeAllDropdowns() {
    document.querySelectorAll('.chat-dropdown.open').forEach(dropdown => {
        dropdown.classList.remove('open');
    });
}

// 문서 클릭 시 드롭다운 닫기
document.addEventListener('click', function (e) {
    if (!e.target.closest('.chat-menu-btn') && !e.target.closest('.chat-dropdown')) {
        closeAllDropdowns();
    }
});

// 페이지 로드 시 채팅 기록 불러오기 + 오래된 대화 정리
document.addEventListener('DOMContentLoaded', function () {
    autoCleanOldChats(); // 20개 초과 시 오래된 대화 삭제
    loadChatHistory(); // 사이드바에 대화 목록 렌더링
});

// 검색 페이지로 이동
function goToSearch() {
    const overlay = document.getElementById('transition-overlay');
    const card = document.getElementById('transition-card');

    if (overlay && card) {
        // 1. 레이어 표시
        overlay.style.display = 'block';

        // 2. 회전 애니메이션 시작
        setTimeout(() => {
            card.style.transform = 'rotateY(180deg)';
        }, 50);

        // 3. 페이지 이동
        setTimeout(() => {
            window.location.href = '/chat/search/';
        }, 1200);
    } else {
        window.location.href = '/chat/search/';
    }
}
