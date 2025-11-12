// src/components/layout/headers/HeaderDashboard.jsx
import React, { useEffect, useState } from "react";
import Messages from "../component/Messages";
import { Link } from "react-router-dom";

export default function HeaderDashboard() {
  // Estado para controlar a abertura/fechamento do popup de mensagens
  const [messageOpen, setMessageOpen] = useState(false);

  // Função genérica para prevenir o comportamento padrão de formulários (não usada diretamente em botões aqui, mas mantida)
  const handleSubmit = (e) => {
    e.preventDefault();
  };

  // Estado para rastrear se o modo tela cheia está ativo
  const [isfullScreen, setIsfullScreen] = useState(false);
  // Estados para controlar a abertura de popups de notificação e perfil (não utilizados no JSX atual)
  const [isOnNotification, setIsOnNotification] = useState(false);
  const [isOnProfile, setIsOnProfile] = useState(false);

  // Estado para armazenar o elemento raiz do documento (<html>)
  const [documentElement, setDocumentElement] = useState();
  
  // Função que alterna entre tela cheia e modo normal
  const handleFullScreenToggle = () => {
    setIsfullScreen((pre) => !pre); // Alterna o estado de tela cheia
    if (!isfullScreen) {
      openFullscreen(); // Entra em tela cheia
    } else {
      closeFullscreen(); // Sai da tela cheia
    }
  };

  // Efeito que executa apenas na montagem para obter o elemento raiz do documento
  useEffect(() => {
    setDocumentElement(document.documentElement);
  }, []);
  
  // Função para solicitar o modo tela cheia usando prefixos de navegadores
  const openFullscreen = () => {
    if (documentElement?.requestFullscreen) {
      documentElement?.requestFullscreen();
    } else if (documentElement?.webkitRequestFullscreen) {
      /* Safari */
      documentElement?.webkitRequestFullscreen();
    } else if (documentElement?.msRequestFullscreen) {
      /* IE11 */
      documentElement?.msRequestFullscreen();
    }
  };

  // Função para alternar entre o modo claro e o modo escuro, adicionando/removendo a classe no <html>
  const handleDarkmode = () => {
    if (document) {
      document.getElementsByTagName("html")[0].classList.toggle("-dark-mode");
    }
  };

  // Função para sair do modo tela cheia usando prefixos de navegadores
  const closeFullscreen = () => {
    if (document?.exitFullscreen) {
      document?.exitFullscreen();
    } else if (document?.webkitExitFullscreen) {
      /* Safari */
      document?.webkitExitFullscreen();
    } else if (document?.msExitFullscreen) {
      /* IE11 */
      document?.msExitFullscreen();
    }
  };

  // Função de manipulação de redimensionamento de janela (vazia, mas usada no useEffect)
  const handleResize = () => {};
  
  // Efeito para esconder o sidebar em telas menores que 990px ao carregar e ao redimensionar
  useEffect(() => {
    // Esconde o sidebar na carga inicial se a tela for pequena
    if (window.innerWidth < 990) {
      document
        .getElementById("dashboardOpenClose")
        .classList.add("-is-sidebar-hidden");
    }
    
    // Função que será chamada no evento 'resize'
    const handleResize = () => {
      if (window.innerWidth < 990) {
        document
          .getElementById("dashboardOpenClose")
          .classList.add("-is-sidebar-hidden");
      }
    };

    // Adiciona o listener de evento para redimensionamento da janela
    window.addEventListener("resize", handleResize);

    // Função de limpeza: remove o listener de evento quando o componente é desmontado
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []); // Executa apenas na montagem e desmontagem
  
  return (
    <>
      {/* Header principal do Dashboard */}
      <header className="header -dashboard -dark-bg-dark-1 js-header">
        <div className="header__container py-20 px-30">
          <div className="row justify-between items-center">
            <div className="col-auto">
              <div className="d-flex items-center">
                {/* Botão de alternância do Sidebar (Menu Lateral) */}
                <div className="header__explore text-dark-1">
                  <button
                    onClick={() => {
                      // Alterna a classe para mostrar/esconder o sidebar
                      document
                        .getElementById("dashboardOpenClose")
                        .classList.toggle("-is-sidebar-hidden");
                    }}
                    className="d-flex items-center js-dashboard-home-9-sidebar-toggle"
                  >
                    <i className="icon -dark-text-white icon-explore"></i>
                  </button>
                </div>

                {/* Logo do site com link para a página inicial */}
                <div className="header__logo ml-30 md:ml-20">
                  <Link data-barba to="/">
                    {/* Imagem do logo (versão clara e escura) */}
                    <img
                      className="-light-d-none"
                      src="/assets/img/general/logo.svg"
                      alt="logo"
                    />
                    <img
                      className="-dark-d-none"
                      src="/assets/img/general/logo-dark.svg"
                      alt="logo"
                    />
                  </Link>
                </div>
              </div>
            </div>

            <div className="col-auto">
              <div className="d-flex items-center">
                {/* Botões de Ações Rápidas (Modo Escuro, Tela Cheia, Mensagens) */}
                <div className="d-flex items-center sm:d-none">
                  {/* Botão de Modo Escuro (Dark Mode) */}
                  <div className="relative">
                    <button
                      onClick={handleDarkmode} // Chama a função que altera o modo escuro
                      className="js-darkmode-toggle text-light-1 d-flex items-center justify-center size-50 rounded-16 -hover-dshb-header-light"
                    >
                      <i className="text-24 icon icon-night"></i>
                    </button>
                  </div>

                  {/* Botão de Tela Cheia (Fullscreen) */}
                  <div className="relative">
                    <button
                      onClick={() => handleFullScreenToggle()} // Chama a função que alterna o modo tela cheia
                      className="d-flex text-light-1 items-center justify-center size-50 rounded-16 -hover-dshb-header-light"
                    >
                      <i className="text-24 icon icon-maximize"></i>
                    </button>
                  </div>

                  {/* Botão de Mensagens/Chat */}
                  <div
                    className="relative"
                    onClick={() => setMessageOpen(true)} // Abre o popup de mensagens
                  >
                    <a
                      href="#"
                      className="d-flex items-center text-light-1 justify-center size-50 rounded-16 -hover-dshb-header-light"
                      data-el-toggle=".js-msg-toggle"
                    >
                      <i className="text-24 icon icon-email"></i>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* Renderiza o componente de Mensagens (popup lateral) */}
        <Messages setMessageOpen={setMessageOpen} messageOpen={messageOpen} />
      </header>
    </>
  );
}