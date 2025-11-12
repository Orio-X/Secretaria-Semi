import React, { useState } from "react";
import Menu from "../component/Menu";
import { Link } from "react-router-dom";

export default function HeaderAuth() {
  return (
    <header className="header -base js-header">
      <div className="header__container py-10">
        <div className="row justify-between items-center">
          <div className="col-auto">
            <div className="header-left">
              <div className="header__logo ">
                <Link data-barba to="/">
                  <img src="/assets/img/general/logo.svg" alt="logo" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
