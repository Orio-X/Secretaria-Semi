import React, { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import axios from 'axios';

// Função para mapear o tipo de evento a uma classe CSS para as cores.
// Essas cores devem corresponder às chaves do seu componente <EventKeys />.
const getEventClassName = (eventType) => {
  switch (eventType) {
    case 'prova':
      return 'fc-event-prova';
    case 'trabalho':
      return 'fc-event-trabalho';
    case 'feriado':
      return 'fc-event-feriado';
    case 'evento':
      return 'fc-event-evento';
    default:
      return 'fc-event-default';
  }
};

export default function EventCalendar() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    // Esta função assíncrona busca os eventos da sua API Django.
    const fetchEvents = async () => {
      try {
        // A URL da sua API. Se você configurou o proxy no vite.config.js,
        // pode usar uma URL relativa como esta.
        const response = await axios.get('/api/eventos-calendario/');
        
        // Mapeamos os dados recebidos do backend para o formato que o FullCalendar entende.
        // O backend envia: { "titulo": "...", "data": "...", "tipo": "..." }
        // FullCalendar precisa de: { title: "...", date: "...", className: "..." }
        const formattedEvents = response.data.map(event => ({
          title: event.titulo,
          date: event.data,
          extendedProps: {
            description: event.descricao,
            type: event.tipo,
          },
          className: getEventClassName(event.tipo)
        }));
        
        setEvents(formattedEvents);

      } catch (error) {
        console.error("Erro ao buscar eventos do calendário:", error);
        // Opcional: Adicionar um estado para mostrar uma mensagem de erro na tela.
      }
    };

    fetchEvents();
  }, []); // O array de dependências vazio [] garante que a busca ocorra apenas uma vez.

  return (
    <>
      {/* Estilos para colorir os eventos no calendário.
        Você pode mover este bloco para seu arquivo CSS principal se preferir.
      */}
      <style>
        {`
          .fc-event-prova, .fc-event-prova .fc-event-main {
            background-color: #35509a;
            border-color: #35509a;
            color: white !important; /* !important para sobrescrever estilos do FullCalendar */
            cursor: pointer;
          }
          .fc-event-trabalho, .fc-event-trabalho .fc-event-main {
            background-color: #f07f00;
            border-color: #f07f00;
            color: white !important;
            cursor: pointer;
          }
          .fc-event-feriado, .fc-event-feriado .fc-event-main {
            background-color: #28a745;
            border-color: #28a745;
            color: white !important;
            cursor: pointer;
          }
          .fc-event-evento, .fc-event-evento .fc-event-main {
            background-color: #6f42c1;
            border-color: #6f42c1;
            color: white !important;
            cursor: pointer;
          }
        `}
      </style>

      <FullCalendar
        plugins={[dayGridPlugin]}
        initialView="dayGridMonth"
        events={events}
        locale="pt-br" // Traduz o calendário para o português
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth' // Você pode adicionar outras visualizações aqui, como 'timeGridWeek,listWeek'
        }}
        buttonText={{
          today: 'Hoje',
          month: 'Mês',
          week: 'Semana',
          list: 'Lista'
        }}
        height="auto" // Ajusta a altura ao conteúdo
        eventClick={(info) => {
          // Ação ao clicar em um evento
          alert(
            `Evento: ${info.event.title}\n` +
            `Data: ${info.event.start.toLocaleDateString('pt-BR')}\n` +
            `Descrição: ${info.event.extendedProps.description || 'Nenhuma descrição'}`
          );
        }}
      />
    </>
  );
}