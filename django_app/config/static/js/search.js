/* =============================================
   청년이음 검색 페이지 JavaScript
   ============================================= */

// ===== 사이드바 토글 =====
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const body = document.body;

    if (window.innerWidth <= 768) {
        // 모바일: 오버레이 모드
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
    } else {
        // 데스크탑: 축소/확장 모드
        sidebar.classList.toggle('collapsed');
        body.classList.toggle('sidebar-collapsed');
    }
}

// ===== 상세검색 토글 =====
function toggleDetailSearch() {
    const panel = document.getElementById('search-filter-panel');
    const btn = document.getElementById('toggle-detail-btn');
    
    panel.classList.toggle('hidden');
    btn.classList.toggle('active');
    
    if (btn.classList.contains('active')) {
        btn.innerHTML = `
            상세검색 닫기
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <path d="M18 15l-6-6-6 6"/>
            </svg>
        `;
    } else {
        btn.innerHTML = `
            상세검색 열기
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <path d="M18 15l-6-6-6 6"/>
            </svg>
        `;
    }
}

// ===== 태그 버튼 토글 (단일 선택) =====
document.addEventListener('DOMContentLoaded', function() {
    // 각 filter-row의 태그 버튼들에 대해 단일 선택 기능 구현
    const filterRows = document.querySelectorAll('.filter-row');
    
    filterRows.forEach(row => {
        const tagButtons = row.querySelectorAll('.tag-btn');
        
        tagButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                // 같은 row 내의 다른 버튼들의 active 제거
                tagButtons.forEach(otherBtn => {
                    otherBtn.classList.remove('active');
                });
                
                // 현재 버튼에 active 추가
                this.classList.add('active');
            });
        });
    });
});

// ===== 내 정보 자동입력 =====
function autoFillUserInfo() {
    // TODO: 실제 구현 시 사용자 정보를 가져와서 입력
    alert('내 정보를 자동으로 입력합니다.');
    
    // 예시: 더미 데이터 입력
    document.querySelector('.filter-select[value=""]').value = 'seoul';
    document.querySelector('input[type="number"].input-underline').value = '25';
}

// ===== 검색 실행 =====
function executeSearch() {
    // 검색어
    const searchQuery = document.querySelector('.main-search-input').value.trim();
    
    // 마감제외 체크박스
    const excludeClosed = document.getElementById('exclude-closed').checked;
    
    // 1. 지역 수집 (첫 번째 선택된 지역의 province 값 사용)
    let region = '';
    if (selectedRegionTags.length > 0) {
        region = selectedRegionTags[0].province; // 예: 'seoul', 'busan'
    }
    
    // 2. 혼인여부
    const maritalStatusSelect = document.querySelectorAll('.filter-select')[0];
    const maritalStatus = maritalStatusSelect ? maritalStatusSelect.value : '';
    
    // 3. 연령
    const ageInput = document.querySelector('input[type="number"].input-underline');
    const age = ageInput ? ageInput.value : '';
    
    // 4. 연소득
    const incomeInputs = document.querySelectorAll('.range-inputs input[type="number"]');
    const incomeMin = incomeInputs[0] ? incomeInputs[0].value : '';
    const incomeMax = incomeInputs[1] ? incomeInputs[1].value : '';
    
    // 5. 학력 (활성화된 태그 버튼들)
    const educationRow = document.querySelectorAll('.filter-row')[2]; // 3번째 filter-row
    const educationTags = Array.from(educationRow.querySelectorAll('.tag-btn.active'))
        .map(btn => btn.textContent.trim());
    
    // 6. 전공요건
    const majorRow = document.querySelectorAll('.filter-row')[3]; // 4번째 filter-row
    const majorTags = Array.from(majorRow.querySelectorAll('.tag-btn.active'))
        .map(btn => btn.textContent.trim());
    
    // 7. 취업상태
    const employmentRow = document.querySelectorAll('.filter-row')[4]; // 5번째 filter-row
    const employmentTags = Array.from(employmentRow.querySelectorAll('.tag-btn.active'))
        .map(btn => btn.textContent.trim());
    
    // 8. 특화분야
    const specializationRow = document.querySelectorAll('.filter-row')[5]; // 6번째 filter-row
    const specializationTags = Array.from(specializationRow.querySelectorAll('.tag-btn.active'))
        .map(btn => btn.textContent.trim());
    
    // API 요청 데이터 구성
    const requestData = {
        query: searchQuery,
        exclude_closed: excludeClosed,
        region: region,
        marital_status: maritalStatus,
        age: age,
        income_min: incomeMin,
        income_max: incomeMax,
        education: educationTags,
        major: majorTags,
        employment_status: employmentTags,
        specialization: specializationTags
    };
    
    console.log('검색 요청 데이터:', requestData);
    
    // API 호출
    fetch('/chat/search-policy/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('검색 결과:', data);
        if (data.error) {
            alert('검색 중 오류가 발생했습니다: ' + data.error);
        } else {
            // 검색 결과 표시
            alert(`검색 완료!\n총 ${data.count}개의 정책을 찾았습니다.`);
            // TODO: 여기에 결과를 표시하는 로직 추가
            displaySearchResults(data.results);
        }
    })
    .catch(error => {
        console.error('검색 오류:', error);
        alert('검색 중 오류가 발생했습니다.');
    });
}

// 검색 결과 표시 함수 (임시)
function displaySearchResults(results) {
    // TODO: 실제 UI에 결과를 표시하는 로직 구현
    console.log('검색 결과 표시:', results);
}

// ===== 필터 초기화 =====
function resetFilters() {
    // 검색어 초기화
    document.querySelector('.main-search-input').value = '';
    
    // 체크박스 초기화
    document.getElementById('exclude-closed').checked = false;
    
    // 셀렉트 박스들 초기화
    document.querySelectorAll('.filter-select').forEach(select => {
        select.selectedIndex = 0;
    });
    
    // 숫자 입력 필드들 초기화
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.value = '';
    });
    
    // 태그 버튼들 초기화 (각 섹션의 첫 번째 버튼 활성화)
    document.querySelectorAll('.filter-row').forEach(row => {
        const tagButtons = row.querySelectorAll('.tag-btn');
        tagButtons.forEach((btn, index) => {
            if (index === 0) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    });
    
    // 지역 선택 초기화
    selectedRegionTags = [];
    currentProvince = null;
    document.getElementById('selected-region-text').textContent = '선택하세요.';
    
    // 지역 모달 내부 상태 초기화
    document.querySelectorAll('#province-list .region-item-clickable').forEach(item => {
        item.classList.remove('active');
    });
    const districtList = document.getElementById('district-list');
    const districtTitle = document.querySelector('.region-column:nth-child(2) .region-column-title');
    districtList.innerHTML = '';
    districtTitle.textContent = '전체';
    document.getElementById('selected-regions-display').innerHTML = '';
}

// ===== 네비게이션 기능들 =====
function handleNewChat() {
    // TODO: chat.html 파일이 만들어지면 해당 URL로 변경
    window.location.href = '/chat/';
}

// ===== 이용 가이드 모달 =====
function openHelpModal() {
    const modal = document.getElementById('help-modal');
    modal.classList.add('active');
}

function closeHelpModal(event) {
    const modal = document.getElementById('help-modal');
    
    // 이벤트가 있고, 모달 내부 클릭이면 닫지 않음
    if (event && event.target !== modal) {
        return;
    }
    
    modal.classList.remove('active');
}

// ===== 지역 선택 모달 =====
const regionData = {
    all: ['전체'],
    seoul: ['전체', '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'],
    busan: ['전체', '강서구', '금정구', '기장군', '남구', '동구', '동래구', '부산진구', '북구', '사상구', '사하구', '서구', '수영구', '연제구', '영도구', '중구', '해운대구'],
    daegu: ['전체', '남구', '달서구', '달성군', '동구', '북구', '서구', '수성구', '중구'],
    incheon: ['전체', '강화군', '계양구', '미추홀구', '남동구', '동구', '부평구', '서구', '연수구', '옹진군', '중구'],
    gwangju: ['전체', '광산구', '남구', '동구', '북구', '서구'],
    daejeon: ['전체', '대덕구', '동구', '서구', '유성구', '중구'],
    ulsan: ['전체', '남구', '동구', '북구', '울주군', '중구'],
    sejong: ['전체'],
    gyeonggi: ['전체', '가평군', '고양시', '과천시', '광명시', '광주시', '구리시', '군포시', '김포시', '남양주시', '동두천시', '부천시', '성남시', '수원시', '시흥시', '안산시', '안성시', '안양시', '양주시', '양평군', '여주시', '연천군', '오산시', '용인시', '의왕시', '의정부시', '이천시', '파주시', '평택시', '포천시', '하남시', '화성시'],
    gangwon: ['전체', '강릉시', '고성군', '동해시', '삼척시', '속초시', '양구군', '양양군', '영월군', '원주시', '인제군', '정선군', '철원군', '춘천시', '태백시', '평창군', '홍천군', '화천군', '횡성군'],
    chungbuk: ['전체', '괴산군', '단양군', '보은군', '영동군', '옥천군', '음성군', '제천시', '증평군', '진천군', '청주시', '충주시'],
    chungnam: ['전체', '계룡시', '공주시', '금산군', '논산시', '당진시', '보령시', '부여군', '서산시', '서천군', '아산시', '예산군', '천안시', '청양군', '태안군', '홍성군'],
    jeonbuk: ['전체', '고창군', '군산시', '김제시', '남원시', '무주군', '부안군', '순창군', '완주군', '익산시', '임실군', '장수군', '전주시', '정읍시', '진안군'],
    jeonnam: ['전체', '강진군', '고흥군', '곡성군', '광양시', '구례군', '나주시', '담양군', '목포시', '무안군', '보성군', '순천시', '신안군', '여수시', '영광군', '영암군', '완도군', '장성군', '장흥군', '진도군', '함평군', '해남군', '화순군'],
    gyeongbuk: ['전체', '경산시', '경주시', '고령군', '구미시', '군위군', '김천시', '문경시', '봉화군', '상주시', '성주군', '안동시', '영덕군', '영양군', '영주시', '영천시', '예천군', '울릉군', '울진군', '의성군', '청도군', '청송군', '칠곡군', '포항시'],
    gyeongnam: ['전체', '거제시', '거창군', '고성군', '김해시', '남해군', '밀양시', '사천시', '산청군', '양산시', '의령군', '진주시', '창녕군', '창원시', '통영시', '하동군', '함안군', '함양군', '합천군'],
    jeju: ['전체', '서귀포시', '제주시']
};

let selectedRegionTags = []; // 선택된 지역 태그들을 저장
let currentProvince = null; // 현재 표시 중인 시/도

function openRegionModal() {
    const modal = document.getElementById('region-modal');
    modal.classList.add('active');
}

function closeRegionModal(event) {
    const modal = document.getElementById('region-modal');
    
    if (event && event.target !== modal) {
        return;
    }
    
    modal.classList.remove('active');
}

// 시/도 클릭 시
function selectProvinceClick(province, provinceName) {
    currentProvince = { value: province, name: provinceName };
    
    // 왼쪽 컬럼 활성화 표시
    document.querySelectorAll('#province-list .region-item-clickable').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`#province-list .region-item-clickable[data-value="${province}"]`).classList.add('active');
    
    // 오른쪽 컬럼 업데이트
    const districtList = document.getElementById('district-list');
    const districtTitle = document.querySelector('.region-column:nth-child(2) .region-column-title');
    
    districtTitle.textContent = provinceName;
    
    if (regionData[province]) {
        districtList.innerHTML = regionData[province].map(district => `
            <div class="region-item-clickable" data-province="${province}" data-district="${district}" onclick="selectDistrictClick('${province}', '${provinceName}', '${district}')">
                ${district}
            </div>
        `).join('');
    }
}

// 시군구 클릭 시
function selectDistrictClick(province, provinceName, district) {
    // 선택된 지역 추가
    const displayText = district === '전체' ? provinceName : `${provinceName} ${district}`;
    
    // 중복 체크
    const exists = selectedRegionTags.find(tag => 
        tag.province === province && tag.district === district
    );
    
    if (!exists) {
        selectedRegionTags.push({
            province: province,
            provinceName: provinceName,
            district: district,
            display: displayText
        });
        
        updateSelectedRegionsDisplay();
    }
}

// 선택된 지역 표시 업데이트
function updateSelectedRegionsDisplay() {
    const selectedDisplay = document.getElementById('selected-regions-display');
    
    if (selectedRegionTags.length === 0) {
        selectedDisplay.innerHTML = '';
    } else {
        selectedDisplay.innerHTML = selectedRegionTags.map((tag, index) => `
            <div class="selected-region-tag">
                <span>${tag.display}</span>
                <span class="remove-tag" onclick="removeSelectedRegionTag(${index})">&times;</span>
            </div>
        `).join('');
    }
}

// 선택된 지역 태그 제거
function removeSelectedRegionTag(index) {
    selectedRegionTags.splice(index, 1);
    updateSelectedRegionsDisplay();
}

// 초기화
function resetRegionSelection() {
    selectedRegionTags = [];
    currentProvince = null;
    
    // 왼쪽 컬럼 활성화 제거
    document.querySelectorAll('#province-list .region-item-clickable').forEach(item => {
        item.classList.remove('active');
    });
    
    // 오른쪽 컬럼 초기화
    const districtList = document.getElementById('district-list');
    const districtTitle = document.querySelector('.region-column:nth-child(2) .region-column-title');
    districtList.innerHTML = '';
    districtTitle.textContent = '전체';
    
    updateSelectedRegionsDisplay();
}

// 적용하기
function applyRegionSelection() {
    const selectedText = document.getElementById('selected-region-text');
    
    if (selectedRegionTags.length === 0) {
        selectedText.textContent = '선택하세요.';
    } else if (selectedRegionTags.length === 1) {
        selectedText.textContent = selectedRegionTags[0].display;
    } else {
        const firstRegion = selectedRegionTags[0].display;
        selectedText.textContent = `${firstRegion} 외 ${selectedRegionTags.length - 1}곳`;
    }
    
    closeRegionModal();
}

// ===== 반응형: 화면 크기 변경 감지 =====
let resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        const body = document.body;
        
        if (window.innerWidth > 768) {
            // 데스크탑 모드로 전환 시 모바일 스타일 제거
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        } else {
            // 모바일 모드로 전환 시 데스크탑 스타일 제거
            body.classList.add('sidebar-collapsed');
        }
    }, 250);
});

// ===== 엔터키로 검색 실행 =====
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.main-search-input');
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                executeSearch();
            }
        });
    }
});
