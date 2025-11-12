import React from "react";
import Menu from "../component/Menu";
import { Link } from "react-router-dom";

import { useState } from "react";

export default function Header() {

  return (
    <>
      <header className="header -type-1 ">
        <div className="header__container">
          <div className="row justify-between items-center">
            <div className="col-auto">
              <div className="header-left">
                <div className="header__logo ">
                  <Link to="/">
                    <img src="/assets/img/general/logo.svg" alt="logo" />
                  </Link>
                </div>
              </div>
            </div>
            <div className="col-auto">
              <div className="header-right d-flex items-center">
                <div className="header-right__buttons d-flex items-center ml-30 md:d-none">
                  <Link
                    to="/login"
                    // AQUI: Classes atualizadas para ficarem iguais ao botão ao lado
                    className="button -md -purple-1 text-white"
                  >
                    Entrar
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>
    </>
  );
}