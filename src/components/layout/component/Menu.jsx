import React from "react";
import { Link } from "react-router-dom";

// REMOVIDO: import { menuList } from "@/data/menu";
// REMOVIDO: useState, useEffect, useLocation

export default function Menu({ allClasses, headerPosition }) {
  // REMOVIDO: Todos os hooks useState, useLocation e useEffect (linhas 9-31)

  return (
    // Contêiner principal do menu (usado para o menu mobile)
    <div
      className={`header-menu js-mobile-menu-toggle ${
        headerPosition ? headerPosition : ""
      }`}
    >
      <div className="header-menu__content">
        <div className="mobile-bg js-mobile-bg"></div>

        {/* Links de Login e Cadastro visíveis apenas em telas grandes (escondidos em XL) */}
        <div className="d-none xl:d-flex items-center px-20 py-20 border-bottom-light">
          <Link to="/login" className="text-dark-1">
            Entrar
          </Link>
        </div>

        {/* Seção principal de navegação do menu */}
        <div className="menu js-navList">
          <ul className={`${allClasses ? allClasses : ""}`}>
            {/* Item do menu: Início */}
            <li className="menu-item-has-children">
              <Link data-barba to="/">
                Inicio
              </Link>
            </li>

            {/* Item do menu: Cursos (com mega menu) */}
            <li className="menu-item-has-children -has-mega-menu">
              <Link data-barba to="#">
                Cursos <i className="icon-chevron-right text-13 ml-10"></i>
              </Link>

              {/* Conteúdo do Mega Menu (visível apenas em telas não XL) */}
              <div className="mega xl:d-none">
                <div className="mega__menu">
                  <div className="row x-gap-40">
                    <div className="col">
                      <h4 className="text-17 fw-500 mb-20">
                        Layouts da Lista de Cursos
                      </h4>

                      <ul className="mega__list">
                        {/* REMOVIDO: O .map() que usava menuList[1] */}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </li>

            {/* Este é um item de menu que provavelmente corresponde a 'Páginas' ou similar */}
            <li className="menu-item-has-children">
              {/* Esta <ul> interna parece agrupar vários submenus/links de nível superior */}
              <ul className="subnav">
                {/* Submenu de Layouts/Páginas */}
                <li className="menu-item-has-children">
                  <ul className="subnav">
                    {/* REMOVIDO: O .map() que usava menuList[4] */}
                  </ul>
                </li>

                {/* Submenu: Contato */}
                <li className="menu-item-has-children">
                  <Link to="#" className="inActiveMenu">
                    Contato<div className="icon-chevron-right text-11"></div>
                  </Link>
                  <ul className="subnav">
                    {/* Botão de voltar no menu mobile */}
                    <li className="menu__backButton js-nav-list-back">
                      <Link to="#">
                        <i className="icon-chevron-left text-13 mr-10"></i>
                        Contato
                      </Link>
                    </li>
                    {/* REMOVIDO: O .map() que usava menuList[4] */}
                  </ul>
                </li>

                {/* Submenu: Shop */}
                <li className="menu-item-has-children">
                  <Link to="#" className="inActiveMenu">
                    Shop<div className="icon-chevron-right text-11"></div>
                  </Link>
                  <ul className="subnav">
                    {/* Botão de voltar no menu mobile */}
                    <li className="menu__backButton js-nav-list-back">
                      <Link to="#">
                        <i className="icon-chevron-left text-13 mr-10"></i> Shop
                      </Link>
                    </li>
                    {/* REMOVIDO: O .map() que usava menuList[4] */}
                  </ul>
                </li>
                {/* REMOVIDO: O .filter() e .map() que usava menuList[4] */}
              </ul>
            </li>
          </ul>
        </div>

        {/* Renderiza o rodapé específico para a visualização mobile */}
      </div>

      {/* Botão para fechar o menu mobile */}
      <div
        className="header-menu-close"
        data-el-toggle=".js-mobile-menu-toggle"
      >
        <div className="size-40 d-flex items-center justify-center rounded-full bg-white">
          <div className="icon-close text-dark-1 text-16"></div>
        </div>
      </div>

      {/* Camada de fundo que escurece quando o menu mobile está aberto */}
      <div className="header-menu-bg"></div>
    </div>
  );
}