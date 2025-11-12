// src/components/dashboard/Sidebar.jsx
import { sidebarItems } from "@/data/dashBoardSidebar";
import React from "react";
import { Link } from "react-router-dom";
import { useLocation } from "react-router-dom";

// --- LÓGICA DE PERMISSÃO (FASE 2) ---

// 1. Lê o 'cargo' salvo no localStorage durante o login
const userCargo = localStorage.getItem('userCargo');

// 2. Define quais links (href) CADA cargo pode ver,
//    baseado na sua lista de regras de negócio.

// Links que TODOS os cargos autenticados podem ver
const commonLinks = [
    '/', // Sair
    '/dshb-calendar', // Calendário
];

// Links específicos para cada cargo
const roleLinks = {
    // --- [CORREÇÃO DE REQUISITO] ---
    // Links da Secretaria atualizados conforme sua nova regra.
    'Secretaria': [
        '/dashboard',           // Controle de Evasão
        '/dshb-administration', // Administração
        '/dshb-notas',          // Painel de desempenho
        '/dshb-emprestimo',     // Gestão de Empréstimos (Regra alterada: DEVE ver)
        // 'Perfil' foi removido
        // 'Planejamento Semanal' foi removido
        // 'Reservas' foi removido
    ],
    'Aluno': [
        '/dshb-settings', // Perfil
        '/dshb-notas',    // Painel de desempenho
    ],
    'Professor': [
        '/dshb-settings',       // Perfil
        '/dshb-planejamento',   // Planejamento Semanal
        '/dshb-administration', // Administração (para Notas/Alunos)
        '/dshb-reservas',       // Reservas
        '/dshb-notas',          // Painel de desempenho (para comentários)
    ],
    'Responsavel': [
        '/dshb-settings', // Perfil
        '/dshb-notas',    // Painel de desempenho
    ],
    'Auxiliar administrativo': [
        '/dshb-administration', // Administração (para Faltas)
        '/dshb-emprestimo',     // Gestão de Empréstimos
        '/dshb-settings',       // Perfil
    ]
};
// --- FIM DA CORREÇÃO ---

// 3. Combina os links comuns com os links do cargo específico
const allowedLinks = [
    ...commonLinks,
    ...(roleLinks[userCargo] || [])
];

// 4. Filtra a lista principal (sidebarItems)
const filteredSidebarItems = sidebarItems.filter(item => 
    allowedLinks.includes(item.href)
);

// --- FIM DA LÓGICA DE PERMISSÃO ---


export default function Sidebar() {
  const { pathname } = useLocation();
  return (
    <div className="sidebar -dashboard">
      
      {/* 5. Renderiza a lista JÁ FILTRADA */}
      {filteredSidebarItems.map((elm, i) => (
        <div
          key={i}
          className={`sidebar__item   ${
            pathname == elm.href ? "-is-active" : ""
          } `}
        >
          <Link
            key={i}
            to={elm.href}
            className="d-flex items-center text-17 lh-1 fw-500 "
          >
            <i className={`${elm.iconClass} mr-15`}></i>
            {elm.text}
          </Link>
        </div>
      ))}
    </div>
  );
}