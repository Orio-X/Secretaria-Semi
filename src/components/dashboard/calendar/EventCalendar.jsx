import React, { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import axios from 'axios';

// Função para mapear o tipo de evento a uma classe CSS para as cores.
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
    const fetchEvents = async () => {
      try {
        const response = await axios.get('/api/eventos-calendario/');
        // Esta linha é útil para ver a estrutura exata que sua API está enviando
        console.log('Dados recebidos da API:', response.data);

        let eventList = [];

        // CORREÇÃO PRINCIPAL AQUI:
        // Verificamos se a resposta é paginada (tem a chave 'results')
        if (response.data && Array.isArray(response.data.results)) {
          eventList = response.data.results;
        } 
        // Senão, verificamos se a resposta já é um array (API não paginada)
        else if (Array.isArray(response.data)) {
          eventList = response.data;
        } 
        // Se não for nenhum dos dois, logamos um erro claro
        else {
          console.error("A resposta da API não é um array nem contém a chave 'results'. Verifique o backend.");
        }

        // Agora usamos a eventList, que garantimos ser um array
        const formattedEvents = eventList.map(event => ({
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
      }
    };

    fetchEvents();
  }, []);

  return (
    <>
      <style>
        {`
          .fc-event-prova, .fc-event-prova .fc-event-main {
            background-color: #35509a;
            border-color: #35509a;
            color: white !important;
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
        locale="pt-br"
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth'
        }}
        buttonText={{
          today: 'Hoje',
          month: 'Mês',
          week: 'Semana',
          list: 'Lista'
        }}
        height="auto"
        eventClick={(info) => {
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