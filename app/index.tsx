import { Calendar, Download, ChevronRight, Info, ExternalLink, ChevronLeft, CalendarPlus } from 'lucide-react';
import React, { useState, useEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';

// --- Data & Configuration ---

// TODO: Github Pages 배포 후 이 URL을 본인의 저장소 주소로 변경해야 합니다.
// 예: 'https://username.github.io/repo-name'
const URL_PATH = '/kbo-calendar-2026'; // Repository Name
const DEPLOY_BASE_URL = `https://kbo-calendar-2026.github.io${URL_PATH}`;

type TeamId = 'all' | 'lg' | 'hanwha' | 'ssg' | 'samsung' | 'nc' | 'kt' | 'lotte' | 'kia' | 'doosan' | 'kiwoom';

interface Team {
  id: TeamId;
  name: string;
  colors: [string, string];
  fontColor: string;
  logoUrl: string;
}

const TEAMS: Team[] = [
  {
    id: 'all',
    name: '전체',
    colors: ['#374151', '#111827'],
    fontColor: '#ffffff',
    logoUrl: `${URL_PATH}/svg/kbo.svg`
  },
  {
    id: 'lg',
    name: 'LG',
    colors: ['#C30452', '#000000'],
    fontColor: '#ffffff',
    logoUrl: `${URL_PATH}/svg/lg.svg`
  },
  {
    id: 'hanwha',
    name: '한화',
    colors: ['#FC4E00', '#07111F'],
    fontColor: '#ffffff',
    logoUrl: `${URL_PATH}/svg/hanwha.svg`
  },
  {
    id: 'samsung',
    name: '삼성',
    colors: ['#074CA1', '#C0C0C0'],
    fontColor: '#ffffff',
    logoUrl: `${URL_PATH}/svg/samsung.svg`
  },
  {
    id: 'ssg',
    name: 'SSG',
    colors: ['#CE0E2D', '#FFB81C'],
    fontColor: '#ffffff',
    logoUrl: `${URL_PATH}/svg/ssg.svg`
  },
  {
    id: 'nc',
    name: 'NC',
    colors: ['#315288', '#AF917B'],
    fontColor: '#ffffff',
    logoUrl: `${URL_PATH}/svg/nc.svg`
  },
  {
    id: 'kt',
    name: 'KT',
    colors: ['#000000', '#EB1C24'],
    fontColor: '#ffffff',
    logoUrl: `${URL_PATH}/svg/kt.svg`
  },
  {
    id: 'lotte',
    name: '롯데',
    colors: ['#041E42', '#D00F31'],
    fontColor: '#ffffff',
    logoUrl: `${URL_PATH}/svg/lotte.svg`
  },
  {
    id: 'kia',
    name: 'KIA',
    colors: ['#EA0029', '#06141F'],
    fontColor: '#ffffff',
    logoUrl: `${URL_PATH}/svg/kia.svg`
  },
  {
    id: 'doosan',
    name: '두산',
    colors: ['#1A1748', '#EB1D25'],
    fontColor: '#ffffff',
    logoUrl: `${URL_PATH}/svg/doosan.svg`
  },
  {
    id: 'kiwoom',
    name: '키움',
    colors: ['#570514', '#B07F4A'],
    fontColor: '#ffffff',
    logoUrl: `${URL_PATH}/svg/kiwoom.svg`
  },
];

// --- Components ---

const App = () => {
  const [selectedTeamId, setSelectedTeamId] = useState<TeamId>('all');
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const guideRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: 'left' | 'right') => {
    if (scrollContainerRef.current) {
      const scrollAmount = 200;
      scrollContainerRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  const selectedTeam = TEAMS.find(t => t.id === selectedTeamId) || TEAMS[0];

  // Dynamic Background Style
  const backgroundStyle = {
    background: selectedTeamId === 'all'
      ? `linear-gradient(135deg, ${selectedTeam.colors[0]}, ${selectedTeam.colors[1]})`
      : `linear-gradient(135deg, ${selectedTeam.colors[0]}cc, ${selectedTeam.colors[1]})`, // slightly transparent to blend
    transition: 'background 0.6s ease-in-out',
  };

  const handleSubscribe = () => {
    let fileName = '';

    if (selectedTeamId === 'all') {
      fileName = 'KBO_League_2026.ics';
    } else {
      fileName = `${selectedTeam.name}_schedule_2026.ics`;
    }

    // 1. 배포된 ICS 파일의 절대 경로 생성
    const fileUrl = `${DEPLOY_BASE_URL}/ics/${fileName}`;

    // 2. 프로토콜을 webcal:// 로 변경하여 구독 요청
    // (http:// -> webcal://, https:// -> webcal://)
    const subscribeUrl = fileUrl.replace(/^https?:\/\//, 'webcal://');

    // 3. 구독 링크 실행
    window.location.href = subscribeUrl;

    // Scroll to Guide Section appropriately
    if (guideRef.current) {
      setTimeout(() => {
        guideRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 500);
    }
  };

  const handleGuideClick = () => {
    window.open('https://blog.naver.com', '_blank'); // Placeholder blog link
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center relative text-gray-800 overflow-hidden">
      {/* Dynamic Background Layer */}
      <div
        className="absolute inset-0 z-0"
        style={backgroundStyle}
      />

      {/* Content Container (Center 1/3, Max-width 480px) */}
      <div className="relative z-10 w-full max-w-[480px] h-screen flex flex-col bg-white/95 shadow-2xl backdrop-blur-sm overflow-hidden transition-all duration-300">

        {/* Header */}
        <header className="px-6 pt-8 pb-4">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">⚾️</span>
            <span className="text-2xl">🏟️</span>
            <h1 className="text-xl font-bold text-gray-900 tracking-tight">KBO 일정 캘린더</h1>
          </div>
          <p className="text-sm text-gray-500 font-medium">
            KBO 2026 시즌. 우리 팀 일정을 캘린더에서 확인하세요. 🙌
          </p>
        </header>

        {/* Tab Navigation (Horizontal Scroll) */}
        <div className="relative w-full border-b border-gray-100 shrink-0">
          {/* Left Desktop Arrow */}
          <button
            onClick={() => scroll('left')}
            className="absolute left-0 top-1/2 -translate-y-1/2 z-20 hidden md:flex items-center justify-center w-8 bg-transparent"
          >
            <ChevronLeft size={20} className="text-gray-400 hover:text-gray-800" />
          </button>

          <div
            ref={scrollContainerRef}
            className="w-full overflow-x-auto no-scrollbar pl-6 py-4"
          >
            <div className="flex gap-3 pr-6 w-max">
              {TEAMS.map((team) => {
                const isActive = selectedTeamId === team.id;
                return (
                  <button
                    key={team.id}
                    onClick={() => setSelectedTeamId(team.id)}
                    style={isActive ? {
                      backgroundColor: team.colors[0],
                      color: team.fontColor,
                    } : {}}
                    className={`
                    whitespace-nowrap px-4 py-2 rounded-[16px] text-sm font-semibold transition-all duration-300
                    ${isActive
                        ? 'shadow-md transform scale-105'
                        : 'bg-gray-100 text-gray-500 hover:bg-gray-200'}
                  `}
                  >
                    {team.name}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Desktop Arrow */}
          <button
            onClick={() => scroll('right')}
            className="absolute right-0 top-1/2 -translate-y-1/2 z-20 hidden md:flex items-center justify-center w-8 bg-transparent"
          >
            <ChevronRight size={20} className="text-gray-400 hover:text-gray-800" />
          </button>
        </div>

        {/* Main Content Area */}
        <main className="flex-1 px-6 py-8 flex flex-col items-center justify-start gap-8 overflow-y-auto no-scrollbar">

          {/* Team Indicator Card (Updated to Logo) */}
          <div className="w-full flex flex-col items-center animate-fade-in">
            <div
              className="w-24 h-24 rounded-[28px] bg-white flex items-center justify-center shadow-lg mb-6 transition-all duration-300 p-4 border border-gray-100"
            >
              <img
                src={selectedTeam.logoUrl}
                alt={`${selectedTeam.name} Logo`}
                className="w-full h-full object-contain"
              />
            </div>

            <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">
              {selectedTeam.name} 경기 일정
            </h2>
            <p className="text-gray-500 text-center text-sm px-4 leading-relaxed">
              {selectedTeamId === 'all'
                ? 'KBO 리그의 모든 경기 일정을 구독하세요.'
                : `${selectedTeam.name}의 2026 정규시즌 모든 경기를 캘린더에 추가합니다.`}
            </p>
          </div>

          {/* Primary Action */}
          <div className="w-full space-y-4">
            <button
              onClick={handleSubscribe}
              className="w-full py-4 px-6 rounded-[16px] flex items-center justify-center gap-3 font-bold text-lg shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300 active:scale-95"
              style={{
                backgroundColor: selectedTeamId === 'all' ? '#1f2937' : selectedTeam.colors[0],
                color: '#ffffff'
              }}
            >
              <CalendarPlus size={22} />
              <span>캘린더 구독하기</span>
            </button>
            <p className="text-xs text-center text-gray-400">
              * 버튼을 누르면 캘린더 앱에 일정이 자동으로 동기화됩니다.
            </p>
          </div>

          {/* Divider */}
          <div className="w-full h-px bg-gray-100 my-2"></div>

          {/* Guide Block (Craft Style Link) */}
          <div className="w-full" ref={guideRef}>
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3 ml-1">
              캘린더 연동 방법
            </h3>
            <button
              onClick={handleGuideClick}
              className="w-full group bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-[16px] p-4 flex items-center justify-between transition-all duration-200 text-left"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-white border border-gray-200 flex items-center justify-center text-gray-600 shadow-sm">
                  <Calendar size={20} />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800 text-sm">캘린더 별 연동 방법</h4>
                  <p className="text-xs text-gray-500 mt-0.5">아이폰, 갤럭시, 구글 캘린더 설정법</p>
                </div>
              </div>
              <ChevronRight size={18} className="text-gray-400 group-hover:text-gray-600 group-hover:translate-x-0.5 transition-transform" />
            </button>
          </div>

        </main>

        {/* Footer */}
        <footer className="p-6 text-center">
          <p className="text-[10px] text-gray-300">
            © 2026 KBO Calendar Project. Unofficial Fan Site.
          </p>
        </footer>
      </div>

      {/* Styles for Hide Scrollbar & Animations */}
      <style>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeIn 0.4s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

const root = createRoot(document.getElementById('root')!);
root.render(<App />);
