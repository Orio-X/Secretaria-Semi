// src/components/dashboard/calendar/Calender.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; 

import FooterNine from "@/components/layout/footers/FooterNine";
import PageLinksTwo from "@/components/common/PageLinksTwo";
import EventCalendar from "./EventCalendar"; 

// --- [PERMISSÃO] Lê o cargo para checagem ---
const userCargo = localStorage.getItem('userCargo');
const canCreateEvents = userCargo === 'Secretaria' || userCargo === 'Auxiliar administrativo';
// -------------------------------------------

export default function Calender() {
  const [isMonthDropdownOpen, setMonthDropdownOpen] = useState(false);
  const [isCourseDropdownOpen, setCourseDropdownOpen] = useState(false);
  const navigate = useNavigate(); 

  const handleNewEventClick = () => {
    navigate('/dshb-listing'); 
  };

  return (
    <div className="dashboard__main">
      <div className="dashboard__content bg-light-4">
        <div className="row pb-50 mb-10">
          <div className="col-auto">
            <h1 className="text-30 lh-12 fw-700">Calendário</h1>
            <PageLinksTwo />
          </div>
        </div>

        <div className="row">
          <div className="col-xl-9 col-lg-9 md:mb-20">
            <div className="col-12">
              <div className="rounded-16 bg-white -dark-bg-dark-1 shadow-4">
                <div className="d-flex items-center py-20 px-30 border-bottom-light">
                  <h2 className="text-17 lh-1 fw-500">Calendário de Eventos</h2>
                </div>

                <div className="py-40 md:py-20 sm:py-10 px-30 md:px-20 sm:px-10">
                  <div className="row y-gap-15 justify-between">
                    <div className="col-auto">
                      
                      {/* --- [PERMISSÃO] O botão só é renderizado se o usuário tiver permissão --- */}
                      {canCreateEvents && (
                        <button 
                          className="button -md -narrow -purple-1 text-white"
                          onClick={handleNewEventClick}
                        >
                          <i className="icon-calendar-2 mr-10"></i>
                          Novo Evento
                        </button>
                      )}
                      {/* ----------------------------------------------------------------- */}

                    </div>
                  </div>

                  
                  <div className="overflow-scroll scroll-bar-1 mt-30">
                    <EventCalendar />
                  </div>      
                </div>
              </div>
            </div>
          </div>    
        </div>
      </div>

      <FooterNine />
    </div>
  );
}